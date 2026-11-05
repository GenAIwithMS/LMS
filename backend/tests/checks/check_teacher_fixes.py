"""Fixes from the teacher panel test report: assignment due dates and total marks, grading
within the total, exam results while marks are missing, attendance only on school days,
no diary or class test marks for days still to come, and remarks in the result sheet.
In-memory SQLite."""
import io, os, shutil, sys, tempfile
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from datetime import timedelta
from src import create_app
from src.db import db, pakistan_time
from src.models import Admin, Teacher, Student, Assignment
import src.services.assignment_submission as submission_service

# Uploaded test files go to a throwaway folder, not the real uploads folder
UPLOADS = tempfile.mkdtemp()
submission_service.UPLOAD_FOLDER = UPLOADS

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
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara"), make(Teacher, "Omar", "omar")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id
    OMAR = Teacher.query.filter_by(username="omar").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara"), "omar": login("omar")}

TODAY = pakistan_time().date()
def day(offset):
    return (TODAY + timedelta(days=offset)).isoformat()

# The last Sunday up to today, and the last school day (Monday to Saturday) up to today
LAST_SUNDAY = TODAY - timedelta(days=TODAY.isoweekday() % 7)
LAST_SCHOOL_DAY = TODAY
while LAST_SCHOOL_DAY.isoweekday() == 7:
    LAST_SCHOOL_DAY = LAST_SCHOOL_DAY - timedelta(days=1)

# Class 5 - A: incharge Sara, who teaches Maths; Omar teaches Science
CLASS_5 = client.get("/api/school/classes", headers=H["root"]).get_json()[4]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
MATHS = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"]).get_json()["subject_id"]
SCIENCE = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Science"}, headers=H["root"]).get_json()["subject_id"]
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": SCIENCE, "teacher_id": OMAR}, headers=H["root"])
for name, uname, roll in [("Ali", "ali", "1"), ("Hina", "hina", "2")]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1",
                                          "section_id": A, "roll_number": roll}, headers=H["root"])
with app.app_context():
    ALI = Student.query.filter_by(username="ali").first().id
    HINA = Student.query.filter_by(username="hina").first().id
H["ali"] = login("ali")


print("--- Assignments: due date and total marks")
homework = {"title": "Fractions", "description": "Ex 2.1", "subject_id": MATHS, "section_id": A, "due_date": day(7), "total_marks": 10}
r = client.post("/api/create/assignments", json=dict(homework, due_date=day(-1)), headers=H["sara"])
check("a due date in the past is refused", r.status_code == 400 and "past" in r.get_json()["message"], r.get_json())
r = client.post("/api/create/assignments", json=dict(homework, total_marks=0), headers=H["sara"])
check("total marks of 0 are refused", r.status_code == 400 and "more than 0" in r.get_json()["message"], r.get_json())
r = client.post("/api/create/assignments", json=homework, headers=H["sara"])
check("an assignment due next week is added", r.status_code in (200, 201), r.get_json())
listed = client.get("/api/get/assignments", headers=H["sara"]).get_json()
if isinstance(listed, dict):
    listed = listed.get("data") or listed.get("assignments") or []
HW = [a for a in listed if a["title"] == "Fractions"][0]
check("the due date is sent as YYYY-MM-DD", HW["due_date"] == day(7), HW["due_date"])

# An old assignment whose due date has passed can still be edited without changing the date
with app.app_context():
    old = Assignment(title="Old work", description="x", teacher_id=SARA, subject_id=MATHS, section_id=A,
                     due_date=TODAY - timedelta(days=30), total_marks=10)
    db.session.add(old)
    db.session.commit()
    OLD = old.id
r = client.put(f"/api/update/assignments/?id={OLD}", json={"title": "Old work (edited)", "due_date": day(-30)}, headers=H["sara"])
check("an old assignment keeps its past due date when edited", r.status_code == 200, r.get_json())
r = client.put(f"/api/update/assignments/?id={OLD}", json={"due_date": day(-2)}, headers=H["sara"])
check("but its due date can't be moved to another past day", r.status_code == 400, r.get_json())


print("--- Grading a submission")
r = client.post("/api/submit/assignment", data={"assignment_id": str(HW["id"]), "submission_text": "my answers",
                                                "submission_file": (io.BytesIO(b"%PDF ali"), "work.pdf")},
                headers=H["ali"], content_type="multipart/form-data")
check("Ali submits", r.status_code == 201, r.get_json())
subs = client.get(f"/api/get/submissions/by/assignment?id={HW['id']}", headers=H["sara"]).get_json()
if isinstance(subs, dict):
    subs = subs.get("data") or subs.get("submissions") or []
SUB = subs[0]["id"]
r = client.put(f"/api/update/submission?id={SUB}", json={"marks_obtained": "15"}, headers=H["sara"])
check("15 out of 10 is refused", r.status_code == 400 and r.get_json()["message"] == "Marks must be between 0 and 10", r.get_json())
r = client.put(f"/api/update/submission?id={SUB}", json={"marks_obtained": "-3"}, headers=H["sara"])
check("negative marks are refused", r.status_code == 400, r.get_json())
r = client.put(f"/api/update/submission?id={SUB}", json={"marks_obtained": "8", "feedback": "Good"}, headers=H["sara"])
check("8 out of 10 is saved", r.status_code == 200, r.get_json())
r = client.put(f"/api/update/assignments/?id={HW['id']}", json={"total_marks": 5}, headers=H["sara"])
check("the total can't go below marks already given", r.status_code == 400, r.get_json())


print("--- Attendance only on school days")
records = [{"student_id": ALI, "status": "present"}, {"student_id": HINA, "status": "present"}]
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": LAST_SUNDAY.isoformat(), "records": records}, headers=H["sara"])
check("a Sunday is refused", r.status_code == 400 and "not a school day" in r.get_json()["message"], r.get_json())
r = client.post(f"/api/school/sections/{A}/attendance", json={"date": LAST_SCHOOL_DAY.isoformat(), "records": records}, headers=H["sara"])
check("a school day is saved", r.status_code == 200, r.get_json())


print("--- Nothing for days still to come")
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": MATHS, "date": day(10), "classwork": "x"}, headers=H["sara"])
check("the diary can't be written for a future date", r.status_code == 400 and "future" in r.get_json()["message"], r.get_json())
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": MATHS, "date": day(0), "classwork": "Fractions"}, headers=H["sara"])
check("today's diary is saved", r.status_code in (200, 201), r.get_json())
r = client.post("/api/school/class-tests", json={"section_id": A, "subject_id": MATHS, "title": "Next week's quiz", "date": day(7), "total_marks": 10}, headers=H["sara"])
check("a test can be planned for next week", r.status_code in (200, 201), r.get_json())
FUTURE_TEST = r.get_json()["test"]["id"] if "test" in r.get_json() else r.get_json().get("test_id")
r = client.put(f"/api/school/class-tests/{FUTURE_TEST}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 7}]}, headers=H["sara"])
check("but its marks can't be entered before that day", r.status_code == 400, r.get_json())


print("--- Exam results while marks are missing")
SESSION = client.post("/api/school/sessions", json={"name": "2026-27", "start_date": day(-200), "end_date": day(160), "is_current": True}, headers=H["root"]).get_json()["session_id"]
TERM = client.post("/api/exams/terms", json={"session_id": SESSION, "name": "First Term", "start_date": day(-14), "end_date": day(-1)}, headers=H["root"]).get_json()["term"]["id"]
client.post(f"/api/exams/terms/{TERM}/papers", json={"class_id": CLASS_5}, headers=H["root"])
P = {paper["subject_name"]: paper["id"] for paper in client.get(f"/api/exams/terms/{TERM}/papers", headers=H["root"]).get_json()}
# Science is marked for both (Hina fails it); Maths only for Ali
client.put(f"/api/exams/papers/{P['Science']}/sections/{A}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 78}, {"student_id": HINA, "obtained_marks": 20}]}, headers=H["omar"])
client.put(f"/api/exams/papers/{P['Maths']}/sections/{A}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 88}]}, headers=H["sara"])
client.put(f"/api/exams/terms/{TERM}/students/{ALI}/remarks", json={"remarks": "Hard working"}, headers=H["sara"])
sheet = client.get(f"/api/exams/terms/{TERM}/sections/{A}/results", headers=H["sara"]).get_json()
rows = {row["name"]: row for row in sheet["students"]}
check("Hina (Maths missing, Science failed) is Incomplete, not Fail", rows["Hina"]["result"] == "Incomplete", rows["Hina"]["result"])
check("and has no position, percentage or grade yet",
      rows["Hina"]["position"] is None and rows["Hina"]["percentage"] is None and rows["Hina"]["grade"] is None, rows["Hina"])
check("Ali (all marked) passes with position 1", rows["Ali"]["result"] == "Pass" and rows["Ali"]["position"] == 1, rows["Ali"])
check("the result sheet carries the incharge's remarks", rows["Ali"]["remarks"] == "Hard working" and rows["Hina"]["remarks"] is None, rows["Ali"].get("remarks"))

shutil.rmtree(UPLOADS, ignore_errors=True)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
