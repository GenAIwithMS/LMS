"""The school timetable: the bell schedule and school days, the admin's draft for every section,
and publishing it to teachers and students. In-memory SQLite."""
import os, sys
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from src import create_app
from src.db import db
from src.models import Admin, Teacher, Student, TimetablePeriod

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

# 5-A and 5-B. In 5-A: Sara teaches Maths, Omar teaches Science, English has no teacher. In 5-B: Omar teaches Maths.
CLASS_5 = client.get("/api/school/classes", headers=H["root"]).get_json()[4]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
B = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B", "incharge_id": OMAR}, headers=H["root"]).get_json()["section_id"]
S = {}
for name in ["Maths", "Science", "English"]:
    S[name] = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": name}, headers=H["root"]).get_json()["subject_id"]
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": S["Maths"], "teacher_id": SARA}, headers=H["root"])
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": S["Science"], "teacher_id": OMAR}, headers=H["root"])
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": S["Maths"], "teacher_id": OMAR}, headers=H["root"])
for name, uname, section in [("Ali", "ali", A), ("Bilal", "bilal", B)]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1", "section_id": section}, headers=H["root"])
H["ali"] = login("ali"); H["bilal"] = login("bilal")

def set_slot(section, day, period, subject, user="root"):
    return client.put(f"/api/school/sections/{section}/timetable", json={"day": day, "period": period, "subject_id": subject}, headers=H[user])

print("--- Bell schedule and school days")
settings = client.get("/api/timetable/settings", headers=H["ali"]).get_json()
check("default: Monday to Saturday, 8 periods with a break after period 4",
      [d["name"] for d in settings["days"]] == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
      and settings["periods_per_day"] == 8 and settings["periods"][4]["is_break"] and settings["periods"][4]["number"] is None, settings["periods"][3:6])
check("each period has its times", settings["periods"][0] == {"number": 1, "name": "Period 1", "start_time": "08:00", "end_time": "08:40", "is_break": False})
def bell(rows):
    result = []
    for name, start, end, is_break in rows:
        result.append({"name": name, "start_time": start, "end_time": end, "is_break": is_break})
    return result
six_periods = bell([("P1", "08:00", "08:45", False), ("P2", "08:45", "09:30", False), ("P3", "09:30", "10:15", False),
                    ("Lunch", "10:15", "10:45", True), ("P4", "10:45", "11:30", False), ("P5", "11:30", "12:15", False), ("P6", "12:15", "13:00", False)])
check("teachers can't change the bell schedule", client.put("/api/timetable/settings", json={"days": [1, 2], "periods": six_periods}, headers=H["sara"]).status_code == 403)
r = client.put("/api/timetable/settings", json={"days": [1], "periods": bell([("P1", "08:00", "08:45", False), ("P2", "08:30", "09:00", False)])}, headers=H["root"])
check("overlapping periods are refused", r.status_code == 400 and "overlap" in r.get_json()["message"], r.get_json())
check("a time like 8:00 is refused (08:00 needed)", client.put("/api/timetable/settings", json={"days": [1], "periods": bell([("P1", "8:00", "08:45", False)])}, headers=H["root"]).status_code == 400)
check("a period must end after it starts", client.put("/api/timetable/settings", json={"days": [1], "periods": bell([("P1", "09:00", "08:45", False)])}, headers=H["root"]).status_code == 400)
check("at least one school day", client.put("/api/timetable/settings", json={"days": [], "periods": six_periods}, headers=H["root"]).status_code == 400)
check("not only breaks", client.put("/api/timetable/settings", json={"days": [1], "periods": bell([("Break", "08:00", "08:30", True)])}, headers=H["root"]).status_code == 400)

print("--- The draft")
check("Maths (Sara) in 5-A, Monday period 1", set_slot(A, 1, 1, S["Maths"]).status_code == 200)
set_slot(A, 1, 8, S["Science"])
set_slot(A, 6, 2, S["English"])
check("teachers can't edit the draft", set_slot(A, 2, 1, S["Maths"], "sara").status_code == 403)
r = client.put("/api/timetable/settings", json={"days": [5, 1, 2, 3, 4], "periods": six_periods}, headers=H["root"])
check("Monday to Friday with 6 periods: Saturday and period 8 leave the draft", r.status_code == 200 and r.get_json()["removed"] == 2, r.get_json())
settings = client.get("/api/timetable/settings", headers=H["root"]).get_json()
check("periods are numbered by time; the lunch break has no number",
      [(p["number"], p["name"]) for p in settings["periods"]] == [(1, "P1"), (2, "P2"), (3, "P3"), (None, "Lunch"), (4, "P4"), (5, "P5"), (6, "P6")]
      and [d["day"] for d in settings["days"]] == [1, 2, 3, 4, 5], settings)
check("Saturday is no longer a school day", set_slot(A, 6, 1, S["Maths"]).status_code == 400)
check("period 7 no longer exists", set_slot(A, 1, 7, S["Maths"]).status_code == 400)
set_slot(A, 1, 2, S["Science"])
set_slot(A, 2, 3, S["English"])
r = set_slot(B, 1, 2, S["Maths"])
check("Omar can't be in 5-B and 5-A at once (he has 5-A Science then)", r.status_code == 409 and "Omar already teaches Science in Class 5 - A" in r.get_json()["message"], r.get_json())
check("5-B Maths (Omar) in period 3 is fine", set_slot(B, 1, 3, S["Maths"]).status_code == 200)
draft = client.get("/api/timetable/draft", headers=H["root"]).get_json()
section_a = [s for s in draft["sections"] if s["section_name"] == "Class 5 - A"][0]
check("the draft has every section with its subjects and teachers",
      [(s["subject_name"], s["teacher_name"]) for s in section_a["subjects"]] == [("English", None), ("Maths", "Sara"), ("Science", "Omar")], section_a["subjects"])
check("each teacher's periods per week", {t["teacher_name"]: t["periods"] for t in draft["teacher_load"]} == {"Omar": 2, "Sara": 1}, draft["teacher_load"])
check("nothing published yet", draft["status"]["is_published"] is False)
check("teachers can't open the whole-school draft", client.get("/api/timetable/draft", headers=H["sara"]).status_code == 403)

print("--- Publishing")
mine = client.get("/api/school/my-timetable", headers=H["ali"]).get_json()
check("before publishing, Ali's timetable is empty", mine["is_published"] is False and mine["slots"] == [])
warnings = client.get("/api/timetable/publish-check", headers=H["root"]).get_json()["warnings"]
check("the check warns about a subject with no teacher", "English in Class 5 - A has no teacher yet" in warnings, warnings)
check("teachers can't publish", client.post("/api/timetable/publish", headers=H["sara"]).status_code == 403)
r = client.post("/api/timetable/publish", headers=H["root"])
check("the admin publishes (warnings don't stop it)", r.status_code == 200 and r.get_json()["publish_status"]["has_unpublished_changes"] is False, r.get_json())
mine = client.get("/api/school/my-timetable", headers=H["ali"]).get_json()
check("Ali now sees 5-A's week with times and teachers",
      mine["is_published"] and sorted((s["day"], s["period"], s["subject_name"], s["teacher_name"]) for s in mine["slots"])
      == [(1, 1, "Maths", "Sara"), (1, 2, "Science", "Omar"), (2, 3, "English", None)] and mine["periods"][0]["start_time"] == "08:00", mine)
sara_week = client.get("/api/school/my-timetable", headers=H["sara"]).get_json()
check("Sara sees only her own periods", [(s["section_name"], s["subject_name"]) for s in sara_week["slots"]] == [("Class 5 - A", "Maths")], sara_week["slots"])
omar_week = client.get("/api/school/my-timetable", headers=H["omar"]).get_json()
check("Omar's week spans both sections", sorted(s["section_name"] for s in omar_week["slots"]) == ["Class 5 - A", "Class 5 - B"])
check("everyone can see when it was published", client.get("/api/timetable/published-info", headers=H["bilal"]).get_json()["is_published"])

print("--- Changes after publishing stay in the draft until published again")
set_slot(A, 3, 1, S["Maths"])
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": S["English"], "teacher_id": SARA}, headers=H["root"])
status = client.get("/api/timetable/draft", headers=H["root"]).get_json()["status"]
check("the admin sees there are unpublished changes", status["is_published"] and status["has_unpublished_changes"], status)
mine = client.get("/api/school/my-timetable", headers=H["ali"]).get_json()
check("Ali still sees the published version (3 periods, English without a teacher)",
      len(mine["slots"]) == 3 and [s["teacher_name"] for s in mine["slots"] if s["subject_name"] == "English"] == [None], mine["slots"])
check("the admin's section view shows the draft (4 periods)", len(client.get(f"/api/school/sections/{A}/timetable", headers=H["root"]).get_json()["slots"]) == 4)
client.post("/api/timetable/publish", headers=H["root"])
mine = client.get("/api/school/my-timetable", headers=H["ali"]).get_json()
check("after publishing again Ali sees the changes", len(mine["slots"]) == 4 and [s["teacher_name"] for s in mine["slots"] if s["subject_name"] == "English"] == ["Sara"])

print("--- A clash stops publishing")
with app.app_context():
    # Put Omar in two places at once directly (the pages never allow this)
    db.session.add(TimetablePeriod(section_id=B, day=1, period=2, subject_id=S["Maths"]))
    db.session.commit()
r = client.post("/api/timetable/publish", headers=H["root"])
check("publishing is refused, naming the clash", r.status_code == 409 and any("Omar is in both" in e for e in r.get_json()["errors"]), r.get_json())
r = client.delete(f"/api/school/sections/{B}/timetable", headers=H["root"])
check("the admin can empty a section's timetable", r.status_code == 200 and client.get(f"/api/school/sections/{B}/timetable", headers=H["root"]).get_json()["slots"] == [])
check("then publishing works", client.post("/api/timetable/publish", headers=H["root"]).status_code == 200)
check("Bilal can't see 5-A's timetable", client.get(f"/api/school/sections/{A}/timetable", headers=H["bilal"]).status_code == 403)

print("--- The subjects each teacher teaches (before any class)")
with app.app_context():
    db.session.add_all([make(Teacher, "Zara", "zara"), make(Teacher, "Kamran", "kamran"), make(Teacher, "Temp", "temp")])
    db.session.commit()
    ZARA = Teacher.query.filter_by(username="zara").first().id
    KAMRAN = Teacher.query.filter_by(username="kamran").first().id
    TEMP = Teacher.query.filter_by(username="temp").first().id
r = client.post(f"/api/school/teachers/{ZARA}/subjects", json={"name": " maths "}, headers=H["root"])
check("a new teacher gets a subject with no class yet (spelling follows the school's Maths)", r.status_code == 201 and "teaches Maths" in r.get_json()["message"], r.get_json())
check("the same subject twice is refused", client.post(f"/api/school/teachers/{ZARA}/subjects", json={"name": "MATHS"}, headers=H["root"]).status_code == 409)
check("a subject no class has yet is fine too", client.post(f"/api/school/teachers/{ZARA}/subjects", json={"name": "Computer"}, headers=H["root"]).status_code == 201)
check("teachers can't change this", client.post(f"/api/school/teachers/{ZARA}/subjects", json={"name": "Art"}, headers=H["sara"]).status_code == 403)
listing = client.get("/api/school/teacher-subjects", headers=H["root"]).get_json()
skills = {t["teacher_name"]: t["subjects"] for t in listing["teachers"]}
check("the list shows each teacher's subjects (Sara's come from what she already teaches)",
      skills["Zara"] == ["Computer", "Maths"] and "Maths" in skills["Sara"] and skills["Kamran"] == [], skills)
check("all subject names, for the picker", "Computer" in listing["subject_names"] and "Science" in listing["subject_names"])
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": S["Science"], "teacher_id": KAMRAN}, headers=H["root"])
skills = {t["teacher_name"]: t["subjects"] for t in client.get("/api/school/teacher-subjects", headers=H["root"]).get_json()["teachers"]}
check("giving a teacher a subject in a section adds it to their subjects", skills["Kamran"] == ["Science"], skills["Kamran"])
draft = client.get("/api/timetable/draft", headers=H["root"]).get_json()
check("the timetable draft lists every teacher with their subjects", {t["teacher_name"]: t["subjects"] for t in draft["teachers"]}["Zara"] == ["Computer", "Maths"])

print("--- Choosing the teacher in a period")
def set_slot_teacher(section, day, period, subject, teacher):
    return client.put(f"/api/school/sections/{section}/timetable", json={"day": day, "period": period, "subject_id": subject, "teacher_id": teacher}, headers=H["root"])
set_slot(A, 4, 1, S["Maths"])                      # Sara: 5-A Maths, Thursday period 1
set_slot(B, 1, 3, S["Maths"])                      # Omar: 5-B Maths, Monday period 3
r = set_slot(B, 4, 1, S["Maths"])
check("5-B Maths (Omar) in Thursday period 1 works (Omar is free)", r.status_code == 200)
set_slot(B, 4, 1, None)
r = set_slot_teacher(B, 4, 1, S["Maths"], SARA)
check("Sara is busy in 5-A then, so she can't take 5-B Maths in that period", r.status_code == 409 and "Sara already teaches Maths in Class 5 - A" in r.get_json()["message"], r.get_json())
r = set_slot_teacher(B, 4, 1, S["Maths"], ZARA)
check("Zara (teaches Maths, free) takes the period and becomes 5-B's Maths teacher",
      r.status_code == 200 and "Zara now teaches Maths in Class 5 - B" in r.get_json()["message"], r.get_json())
slots_b = client.get(f"/api/school/sections/{B}/timetable", headers=H["root"]).get_json()["slots"]
check("all of 5-B's Maths periods are Zara's now", sorted((s["day"], s["period"], s["teacher_name"]) for s in slots_b if s["subject_name"] == "Maths") == [(1, 3, "Zara"), (4, 1, "Zara")], slots_b)
set_slot(B, 2, 3, S["Maths"])                      # Zara: 5-B Maths, Tuesday period 3 (5-A has English then)
r = set_slot_teacher(A, 5, 1, S["English"], ZARA)
check("Zara can't take over 5-A English: she's in 5-B during its Tuesday period", r.status_code == 409 and "can't take over English" in r.get_json()["message"], r.get_json())
check("nothing changed after the refusal", [s for s in client.get(f"/api/school/sections/{A}/timetable", headers=H["root"]).get_json()["slots"] if s["day"] == 5] == [])
check("the period's teacher must exist", set_slot_teacher(A, 5, 1, S["Maths"], 99999).status_code == 400)

print("--- Removing a teacher's subject, deleting a teacher")
r = client.delete(f"/api/school/teachers/{ZARA}/subjects?name=Maths", headers=H["root"])
check("a subject they still teach in a section can't be removed", r.status_code == 409 and "Class 5 - B" in r.get_json()["message"], r.get_json())
check("one they don't teach anywhere can", client.delete(f"/api/school/teachers/{ZARA}/subjects?name=computer", headers=H["root"]).status_code == 200)
client.post(f"/api/school/teachers/{TEMP}/subjects", json={"name": "Art"}, headers=H["root"])
check("a teacher with subjects (but no classes) can still be deleted", client.delete(f"/api/delete/teacher?id={TEMP}", headers=H["root"]).status_code == 200)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
