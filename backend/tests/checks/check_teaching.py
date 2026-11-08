"""Teaching (Phase 2): daily attendance by the class incharge, syllabus progress, the diary,
assignments per section, class tests, and the timetable with its clash check. In-memory SQLite."""
import os, sys
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # for school_setup
from school_setup import make_every_day_a_school_day

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from datetime import timedelta
from src import create_app
from src.db import db, pakistan_time
from src.models import Admin, Teacher, Student

app = create_app()
client = app.test_client()
fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond:
        fails.append(name)

def make(cls, name, uname, **kw):
    u = cls(name=name, username=uname, email=f"{uname}@x.com", **kw); u.set_password("secret1"); return u

with app.app_context():
    db.create_all()
    make_every_day_a_school_day()   # attendance for "today" works on any day
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara"), make(Teacher, "Omar", "omar"), make(Teacher, "Zara", "zara")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id
    OMAR = Teacher.query.filter_by(username="omar").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara"), "omar": login("omar"), "zara": login("zara")}

TODAY = pakistan_time().date()
YESTERDAY = (TODAY - timedelta(days=1)).isoformat()
TOMORROW = (TODAY + timedelta(days=1)).isoformat()
TODAY = TODAY.isoformat()

# School: 5-A (incharge Sara) and 5-B (incharge Omar).
# Sara teaches Maths in 5-A. Omar teaches Science in 5-A and Maths in 5-B.
CLASS_5 = client.get("/api/school/classes", headers=H["root"]).get_json()[4]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
B = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B", "incharge_id": OMAR}, headers=H["root"]).get_json()["section_id"]
MATHS = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"]).get_json()["subject_id"]
SCIENCE = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Science"}, headers=H["root"]).get_json()["subject_id"]
ENGLISH = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "English"}, headers=H["root"]).get_json()["subject_id"]
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": SCIENCE, "teacher_id": OMAR}, headers=H["root"])
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": MATHS, "teacher_id": OMAR}, headers=H["root"])
CHAPTERS = []
for title in ["Numbers", "Fractions", "Decimals", "Geometry"]:
    # 5-A's Maths teacher writes 5-A's syllabus
    CHAPTERS.append(client.post(f"/api/school/sections/{A}/subjects/{MATHS}/chapters", json={"title": title}, headers=H["sara"]).get_json()["chapter"]["id"])
for name, uname, section, roll in [("Ali", "ali", A, "1"), ("Hina", "hina", A, "2"), ("Bilal", "bilal", B, "1")]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1",
                                          "section_id": section, "roll_number": roll}, headers=H["root"])
with app.app_context():
    ALI = Student.query.filter_by(username="ali").first().id
    HINA = Student.query.filter_by(username="hina").first().id
    BILAL = Student.query.filter_by(username="bilal").first().id
H["ali"] = login("ali"); H["bilal"] = login("bilal")

print("--- Daily attendance (class incharge only)")
r = client.get(f"/api/school/sections/{A}/attendance", headers=H["sara"])
register = r.get_json()
check("Sara opens today's register for 5-A, nobody marked yet",
      r.status_code == 200 and [s["name"] for s in register["students"]] == ["Ali", "Hina"] and not register["is_marked"], register)
day_records = [{"student_id": ALI, "status": "present"}, {"student_id": HINA, "status": "absent"}]
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TODAY, "records": day_records}, headers=H["sara"])
check("Sara (incharge) marks 5-A", r.status_code == 200, r.get_json())
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TODAY, "records": day_records}, headers=H["omar"])
check("Omar teaches in 5-A but isn't its incharge, so he can't mark it", r.status_code == 403, r.get_json())
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TODAY, "records": day_records}, headers=H["root"])
check("the admin doesn't mark attendance either", r.status_code == 403)
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TODAY, "records": [{"student_id": BILAL, "status": "present"}]}, headers=H["sara"])
check("a student of another section can't be marked in 5-A", r.status_code == 400, r.get_json())
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TOMORROW, "records": day_records}, headers=H["sara"])
check("no attendance for a future date", r.status_code == 400, r.get_json())
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TODAY, "records": [{"student_id": ALI, "status": "sleeping"}]}, headers=H["sara"])
check("unknown status is refused", r.status_code == 400)
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": TODAY, "records": [{"student_id": HINA, "status": "late"}]}, headers=H["sara"])
register = client.get(f"/api/school/sections/{A}/attendance?date={TODAY}", headers=H["sara"]).get_json()
check("marking the same day again updates it (no duplicates)",
      r.status_code == 200 and {s["name"]: s["status"] for s in register["students"]} == {"Ali": "present", "Hina": "late"} and register["is_marked"], register)
client.post(f"/api/school/sections/{A}/attendance", json={"date": YESTERDAY, "records": [{"student_id": ALI, "status": "absent"}, {"student_id": HINA, "status": "present"}]}, headers=H["sara"])
check("Omar (teaches in 5-A) can view the register", client.get(f"/api/school/sections/{A}/attendance", headers=H["omar"]).status_code == 200)
check("Zara (not in 5-A) can't view it", client.get(f"/api/school/sections/{A}/attendance", headers=H["zara"]).status_code == 403)
check("a student can't open the section register", client.get(f"/api/school/sections/{A}/attendance", headers=H["ali"]).status_code == 403)
check("a bad date is refused", client.get(f"/api/school/sections/{A}/attendance?date=yesterday", headers=H["sara"]).status_code == 400)
mine = client.get("/api/school/my-attendance", headers=H["ali"]).get_json()
check("Ali sees his own days and percentage (1 present, 1 absent = 50%)",
      len(mine["records"]) == 2 and mine["summary"]["present"] == 1 and mine["summary"]["absent"] == 1 and mine["summary"]["percentage"] == 50.0, mine["summary"])
summary = client.get(f"/api/school/sections/{A}/attendance/summary?month={TODAY[:7]}", headers=H["sara"]).get_json()
hina_row = [s for s in summary["students"] if s["name"] == "Hina"][0]
check("month summary: late counts as attended", hina_row["late"] == 1 and hina_row["percentage"] == 100.0 if YESTERDAY[:7] == TODAY[:7] else hina_row["late"] == 1, hina_row)
check("a bad month is refused", client.get(f"/api/school/sections/{A}/attendance/summary?month=13-2026", headers=H["sara"]).status_code == 400)

# Back to the normal school week (Monday to Saturday) for the timetable checks below
with app.app_context():
    from src.models import SchoolSetting
    SchoolSetting.query.filter_by(key="school_days").first().value = "1,2,3,4,5,6"
    db.session.commit()

print("--- Syllabus progress (subject teacher)")
r = client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[0]}/progress", json={"status": "done"}, headers=H["sara"])
check("Sara marks chapter 1 done in 5-A", r.status_code == 200, r.get_json())
client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[1]}/progress", json={"status": "in_progress", "planned_date": TOMORROW}, headers=H["sara"])
r = client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[2]}/progress", json={"status": "done"}, headers=H["omar"])
check("Omar doesn't teach Maths in 5-A, so he can't update it", r.status_code == 403)
r = client.put(f"/api/school/sections/{B}/chapters/{CHAPTERS[0]}/progress", json={"status": "done"}, headers=H["sara"])
check("Sara can't update 5-B's Maths", r.status_code == 403)
progress = client.get(f"/api/school/sections/{A}/subjects/{MATHS}/progress", headers=H["ali"]).get_json()
statuses = [c["status"] for c in progress["chapters"]]
check("Ali sees 5-A Maths: 1 of 4 done (25%), chapter 2 in progress with dates",
      statuses == ["done", "in_progress", "not_started", "not_started"] and progress["percentage"] == 25
      and progress["chapters"][0]["completed_on"] == TODAY and progress["chapters"][1]["planned_date"] == TOMORROW, progress)
b_progress = client.get(f"/api/school/sections/{B}/subjects/{MATHS}/progress", headers=H["omar"]).get_json()
check("5-B's progress is separate (0%)", b_progress["percentage"] == 0, b_progress.get("percentage"))
client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[0]}/progress", json={"status": "not_started"}, headers=H["sara"])
progress = client.get(f"/api/school/sections/{A}/subjects/{MATHS}/progress", headers=H["sara"]).get_json()
check("back to not started clears the dates", progress["chapters"][0]["completed_on"] is None and progress["chapters"][0]["started_on"] is None)
client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[0]}/progress", json={"status": "done"}, headers=H["sara"])
overview = client.get(f"/api/school/sections/{A}/progress", headers=H["root"]).get_json()
maths_row = [s for s in overview["subjects"] if s["subject_name"] == "Maths"][0]
check("the section overview shows each subject's coverage", maths_row["done_count"] == 1 and maths_row["in_progress_count"] == 1 and maths_row["teacher_name"] == "Sara", maths_row)
check("Bilal (5-B) can't see 5-A's progress", client.get(f"/api/school/sections/{A}/progress", headers=H["bilal"]).status_code == 403)

print("--- Daily diary (subject teacher)")
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": MATHS, "date": TODAY, "classwork": "Fractions p.12", "homework": "Ex 2.1 Q1-5"}, headers=H["sara"])
check("Sara writes today's Maths diary for 5-A", r.status_code == 201, r.get_json())
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": MATHS, "date": TODAY, "classwork": "Fractions p.12-13", "homework": "Ex 2.1 all"}, headers=H["sara"])
check("writing it again updates the same entry", r.status_code == 200, r.get_json())
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": SCIENCE, "date": TODAY, "homework": "Read ch 3"}, headers=H["sara"])
check("Sara can't write the Science diary", r.status_code == 403)
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": SCIENCE, "date": TODAY, "homework": "Read ch 3"}, headers=H["omar"])
check("Omar writes the Science diary", r.status_code == 201)
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": SCIENCE, "date": TODAY}, headers=H["omar"])
check("an empty diary entry is refused", r.status_code == 400)
diary = client.get(f"/api/school/sections/{A}/diary?date={TODAY}", headers=H["ali"]).get_json()
check("Ali reads 5-A's diary for today, by subject",
      [(e["subject_name"], e["homework"]) for e in diary["entries"]] == [("Maths", "Ex 2.1 all"), ("Science", "Read ch 3")], diary)
check("Bilal can't read 5-A's diary", client.get(f"/api/school/sections/{A}/diary", headers=H["bilal"]).status_code == 403)
science_entry = diary["entries"][1]["id"]
check("Sara can't delete Omar's Science entry", client.delete(f"/api/school/diary/{science_entry}", headers=H["sara"]).status_code == 403)
check("Omar deletes his entry", client.delete(f"/api/school/diary/{science_entry}", headers=H["omar"]).status_code == 200)

print("--- Assignments per section")
assignment = {"title": "Fractions worksheet", "description": "Do it", "due_date": TOMORROW, "subject_id": MATHS, "total_marks": "10"}
r = client.post("/api/create/assignments", json=assignment, headers=H["sara"])
check("Sara's assignment goes to 5-A by itself (she teaches Maths only there)", r.status_code == 201, r.get_json())
listed = client.get("/api/get/assignments", headers=H["sara"]).get_json()["assignments"]
check("the assignment shows its section", listed[0]["section_name"] == "Class 5 - A", listed[0])
r = client.post("/api/create/assignments", json=dict(assignment, section_id=B), headers=H["sara"])
check("Sara can't set Maths work for 5-B", r.status_code == 403, r.get_json())
r = client.post("/api/create/assignments", json=dict(assignment, title="5-B work", section_id=B), headers=H["omar"])
check("Omar sets Maths work for 5-B", r.status_code == 201, r.get_json())
ali_sees = [a["title"] for a in client.get("/api/get/assignments", headers=H["ali"]).get_json()["assignments"]]
bilal_sees = [a["title"] for a in client.get("/api/get/assignments", headers=H["bilal"]).get_json()["assignments"]]
check("each section's students only see their own section's work", ali_sees == ["Fractions worksheet"] and bilal_sees == ["5-B work"], (ali_sees, bilal_sees))
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": SCIENCE, "teacher_id": OMAR}, headers=H["root"])
r = client.post("/api/create/assignments", json=dict(assignment, title="Science", subject_id=SCIENCE), headers=H["omar"])
check("a teacher who teaches a subject in two sections must choose the section", r.status_code == 400 and "Choose the section" in r.get_json()["message"], r.get_json())
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": SCIENCE, "teacher_id": None}, headers=H["root"])

print("--- Class tests")
r = client.post("/api/school/class-tests", json={"section_id": A, "subject_id": MATHS, "title": "Quiz 1", "date": TODAY, "total_marks": 10, "chapter_id": CHAPTERS[0]}, headers=H["sara"])
check("Sara adds a Maths quiz in 5-A", r.status_code == 201, r.get_json())
TEST = r.get_json()["test"]["id"]
r = client.post("/api/school/class-tests", json={"section_id": B, "subject_id": MATHS, "title": "Quiz", "date": TODAY, "total_marks": 10}, headers=H["sara"])
check("Sara can't add a test for 5-B", r.status_code == 403)
r = client.post("/api/school/class-tests", json={"section_id": A, "subject_id": MATHS, "title": "Quiz", "date": TODAY, "total_marks": 10, "chapter_id": 99999}, headers=H["sara"])
check("the chapter must belong to the subject", r.status_code == 400)
r = client.put(f"/api/school/class-tests/{TEST}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 8.5}, {"student_id": HINA, "obtained_marks": None}]}, headers=H["sara"])
check("Sara enters marks (Hina absent)", r.status_code == 200, r.get_json())
r = client.put(f"/api/school/class-tests/{TEST}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 11}]}, headers=H["sara"])
check("marks can't be more than the total", r.status_code == 400, r.get_json())
r = client.put(f"/api/school/class-tests/{TEST}/marks", json={"marks": [{"student_id": BILAL, "obtained_marks": 5}]}, headers=H["sara"])
check("a student of another section can't get marks", r.status_code == 400)
r = client.put(f"/api/school/class-tests/{TEST}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 5}]}, headers=H["omar"])
check("Omar can't enter Maths marks in 5-A", r.status_code == 403)
details = client.get(f"/api/school/class-tests/{TEST}", headers=H["sara"]).get_json()
check("the test shows every student with marks, and the average",
      [(s["name"], s["obtained_marks"]) for s in details["students"]] == [("Ali", "8.5"), ("Hina", None)] and details["average"] == 8.5, details)
check("the admin can see the marks", client.get(f"/api/school/class-tests/{TEST}", headers=H["root"]).status_code == 200)
check("Zara can't see the marks", client.get(f"/api/school/class-tests/{TEST}", headers=H["zara"]).status_code == 403)
check("Sara lists her tests", [t["title"] for t in client.get("/api/school/class-tests", headers=H["sara"]).get_json()] == ["Quiz 1"])
check("Omar's list doesn't include Sara's test", client.get("/api/school/class-tests", headers=H["omar"]).get_json() == [])
ali_tests = client.get("/api/school/class-tests", headers=H["ali"]).get_json()
check("Ali sees the quiz with his own marks", ali_tests[0]["my_marks"] == "8.5" and not ali_tests[0]["was_absent"], ali_tests)
r = client.put(f"/api/school/class-tests/{TEST}", json={"total_marks": 5}, headers=H["sara"])
check("the total can't drop below marks already given", r.status_code == 400)
check("the subject can't be deleted while it has tests", client.delete(f"/api/school/subjects/{MATHS}", headers=H["root"]).status_code == 409)

print("--- Timetable and the clash check")
r = client.put(f"/api/school/sections/{A}/timetable", json={"day": 1, "period": 1, "subject_id": SCIENCE}, headers=H["root"])
check("admin puts Science (Omar) in 5-A, Monday period 1", r.status_code == 200, r.get_json())
r = client.put(f"/api/school/sections/{B}/timetable", json={"day": 1, "period": 1, "subject_id": MATHS}, headers=H["root"])
check("Omar can't also be in 5-B in the same period", r.status_code == 409 and "Omar already teaches Science in Class 5 - A" in r.get_json()["message"], r.get_json())
r = client.put(f"/api/school/sections/{B}/timetable", json={"day": 1, "period": 2, "subject_id": MATHS}, headers=H["root"])
check("5-B Maths (Omar) in period 2 is fine", r.status_code == 200)
r = client.put(f"/api/school/sections/{A}/timetable", json={"day": 1, "period": 2, "subject_id": MATHS}, headers=H["root"])
check("5-A Maths (Sara) in period 2 is fine too", r.status_code == 200)
r = client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": OMAR}, headers=H["root"])
check("giving 5-A Maths to Omar is refused: he's in 5-B in period 2", r.status_code == 409, r.get_json())
r = client.put(f"/api/school/sections/{A}/timetable", json={"day": 1, "period": 3, "subject_id": ENGLISH}, headers=H["root"])
check("a subject with no teacher yet can still go in the timetable", r.status_code == 200)
r = client.put(f"/api/school/sections/{A}/timetable", json={"day": 7, "period": 1, "subject_id": MATHS}, headers=H["root"])
check("only Monday to Saturday", r.status_code == 400)
r = client.put(f"/api/school/sections/{A}/timetable", json={"day": 2, "period": 1, "subject_id": MATHS}, headers=H["sara"])
check("teachers can't change the timetable", r.status_code == 403)
check("before publishing, students see no timetable", client.get(f"/api/school/sections/{A}/timetable", headers=H["ali"]).get_json()["slots"] == [])
client.post("/api/timetable/publish", headers=H["root"])
table = client.get(f"/api/school/sections/{A}/timetable", headers=H["ali"]).get_json()
check("Ali sees 5-A's week with teachers", [(s["period"], s["subject_name"], s["teacher_name"]) for s in table["slots"]] == [(1, "Science", "Omar"), (2, "Maths", "Sara"), (3, "English", None)], table["slots"])
omar_week = client.get("/api/school/my-timetable", headers=H["omar"]).get_json()
check("Omar's own week spans both sections", [(s["period"], s["section_name"]) for s in omar_week["slots"]] == [(1, "Class 5 - A"), (2, "Class 5 - B")], omar_week["slots"])
check("Ali's my-timetable is his section's", len(client.get("/api/school/my-timetable", headers=H["ali"]).get_json()["slots"]) == 3)
r = client.put(f"/api/school/sections/{A}/timetable", json={"day": 1, "period": 3, "subject_id": None}, headers=H["root"])
check("a period can be emptied", r.status_code == 200 and len(client.get(f"/api/school/sections/{A}/timetable", headers=H["root"]).get_json()["slots"]) == 2)
check("Bilal can't see 5-A's timetable", client.get(f"/api/school/sections/{A}/timetable", headers=H["bilal"]).status_code == 403)

print("--- Safe deletes")
r = client.delete(f"/api/school/chapters/{CHAPTERS[0]}", headers=H["sara"])
check("deleting a chapter keeps its test (without the chapter)", r.status_code == 200 and client.get(f"/api/school/class-tests/{TEST}", headers=H["sara"]).get_json()["chapter_id"] is None)
check("a test can be deleted by its teacher", client.delete(f"/api/school/class-tests/{TEST}", headers=H["sara"]).status_code == 200)
EMPTY = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "C"}, headers=H["root"]).get_json()["section_id"]
client.put(f"/api/school/sections/{EMPTY}/timetable", json={"day": 2, "period": 1, "subject_id": ENGLISH}, headers=H["root"])
check("an empty section with only a timetable can be deleted", client.delete(f"/api/school/sections/{EMPTY}", headers=H["root"]).status_code == 200)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
