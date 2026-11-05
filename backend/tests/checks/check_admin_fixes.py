"""Fixes from the admin panel test report: logout/stay twice, deleting students and teachers
with clear messages, roll numbers unique in a section, events in the past, positions only
for complete results, editing and deleting sessions, and plural wording. In-memory SQLite."""
import os, sys
from datetime import date, time, timedelta
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
from src.models import Admin, Teacher, Student, DailyAttendance, AcademicSession, Event
from src.services.wording import plural
from src.services.exam_results import add_positions
from src.services.event import time_text

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
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara"), make(Teacher, "Zara", "zara")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id
    ZARA = Teacher.query.filter_by(username="zara").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara")}

# Class 5: 5-A (incharge Sara). Class 6: 6-A.
classes = client.get("/api/school/classes", headers=H["root"]).get_json()
CLASS_5 = classes[4]["id"]; CLASS_6 = classes[5]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
SIX_A = client.post(f"/api/school/classes/{CLASS_6}/sections", json={"name": "A"}, headers=H["root"]).get_json()["section_id"]

def add_student(name, uname, section, roll):
    return client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1",
                                                 "section_id": section, "roll_number": roll}, headers=H["root"])

def student_id(uname):
    with app.app_context():
        return Student.query.filter_by(username=uname).first().id


# ---------------- H2: "stay logged in" sent twice must not fail
r1 = client.post("/api/logout/stay", headers=H["sara"])
r2 = client.post("/api/logout/stay", headers=H["sara"])
check("logout/stay works when sent twice", r1.status_code < 500 and r2.status_code < 500, (r1.status_code, r2.status_code))


# ---------------- M3: roll numbers unique in a section
r = add_student("Ali", "ali", A, "1")
check("Ali added with roll 1", r.status_code in (200, 201), r.get_json())
r = add_student("Hina", "hina", A, "1")
check("a second roll 1 in 5-A is refused", r.status_code in (400, 409) and "Roll number 1" in r.get_json()["message"], r.get_json())
r = add_student("Hina", "hina", A, "2")
check("Hina added with roll 2", r.status_code in (200, 201), r.get_json())
r = client.put(f"/api/update/student?id={student_id('hina')}", json={"roll_number": "1"}, headers=H["root"])
check("changing Hina to roll 1 is refused", r.status_code in (400, 409), r.get_json())
r = client.put(f"/api/update/student?id={student_id('hina')}", json={"roll_number": "2"}, headers=H["root"])
check("saving Hina with her own roll number works", r.status_code == 200, r.get_json())
r = add_student("Kamal", "kamal", SIX_A, "1")
check("roll 1 can be used again in another section", r.status_code in (200, 201), r.get_json())

# Promotion: Ali (roll 1) moves to 6-A, where Kamal has roll 1, so Ali's roll is cleared
r = client.post(f"/api/exams/promotion/sections/{A}", json={"target_section_id": SIX_A, "student_ids": [student_id("ali")]}, headers=H["root"])
body = r.get_json()
check("promotion works", r.status_code == 200, body)
check("promotion message is singular", body["message"].startswith("1 student promoted"), body["message"])
check("promotion says a roll number must be chosen again", body.get("roll_numbers_cleared") == 1, body)
with app.app_context():
    check("Ali's clashing roll number was cleared", Student.query.get(student_id("ali")).roll_number in (None, ""))


# ---------------- M2: deleting a student with records
with app.app_context():
    db.session.add(DailyAttendance(student_id=student_id("hina"), section_id=A, date=date.today(), status="present"))
    db.session.commit()
r = client.get(f"/api/admin/students/{student_id('hina')}/delete-check", headers=H["root"])
check("the delete check lists Hina's attendance", r.status_code == 200 and r.get_json()["records"][0]["label"] == "1 day of attendance", r.get_json())
r = client.get(f"/api/admin/students/{student_id('hina')}/delete-check", headers=H["sara"])
check("a teacher can't use the delete check", r.status_code in (401, 403))
r = client.delete(f"/api/delete/student?id={student_id('hina')}", headers=H["root"])
check("deleting a student with records needs confirming", r.status_code == 409 and "attendance" in r.get_json()["message"], r.get_json())
HINA = student_id("hina")
r = client.delete(f"/api/delete/student?id={HINA}&remove_records=true", headers=H["root"])
check("deleting with remove_records works", r.status_code == 200, r.get_json())
with app.app_context():
    check("Hina and her attendance are gone", Student.query.get(HINA) is None and DailyAttendance.query.filter_by(student_id=HINA).count() == 0)
r = client.delete(f"/api/delete/student?id={student_id('kamal')}", headers=H["root"])
check("a student with no records is deleted straight away", r.status_code == 200, r.get_json())


# ---------------- M2: deleting a teacher
r = client.get(f"/api/admin/teachers/{SARA}/delete-check", headers=H["root"])
body = r.get_json()
check("Sara can't be deleted while she leads 5-A", r.status_code == 200 and body["can_delete"] is False and "5" in body["blockers"][0], body)
r = client.delete(f"/api/delete/teacher?id={SARA}", headers=H["root"])
check("deleting Sara is refused with the reason", r.status_code == 409 and "class incharge" in r.get_json()["message"], r.get_json())
r = client.get(f"/api/admin/teachers/{ZARA}/delete-check", headers=H["root"])
check("Zara (teaches nothing) can be deleted", r.get_json()["can_delete"] is True, r.get_json())
r = client.delete(f"/api/delete/teacher?id={ZARA}", headers=H["root"])
check("Zara is deleted", r.status_code == 200, r.get_json())


# ---------------- L3: events
yesterday = (date.today() - timedelta(days=2)).isoformat()
next_week = (date.today() + timedelta(days=7)).isoformat()
r = client.post("/api/create/event", json={"title": "Old trip", "event_date": yesterday}, headers=H["root"])
check("an event in the past is refused", r.status_code == 400 and "past" in r.get_json()["message"], r.get_json())
r = client.post("/api/create/event", json={"title": "Sports day", "event_date": next_week, "event_time": "09:00:00"}, headers=H["root"])
check("an event next week is added", r.status_code in (200, 201), r.get_json())
events = client.get("/api/get/events", headers=H["root"]).get_json()
if isinstance(events, dict):
    events = events.get("data", [])
sports = [e for e in events if e["title"] == "Sports day"]
check("event time shows without seconds", len(sports) == 1 and sports[0]["event_time"] == "09:00", sports)
check("time_text of no time is None", time_text(None) is None)
check("time_text drops seconds", time_text(time(14, 30, 0)) == "14:30")


# ---------------- L9: no position while marks are missing
results = [
    {"total_obtained": "90", "percentage": 90, "result": "Pass"},
    {"total_obtained": "95", "percentage": None, "result": "Incomplete"},
    {"total_obtained": "80", "percentage": 80, "result": "Incomplete"},
    {"total_obtained": "70", "percentage": 70, "result": "Pass"},
]
add_positions(results)
check("complete results are ranked 1 and 2", results[0].get("position") == 1 and results[3].get("position") == 2, results)
check("incomplete results get no position", "position" not in results[1] and "position" not in results[2], results)


# ---------------- L10: editing and deleting sessions
# The first session becomes the current one, so add two
client.post("/api/school/sessions", json={"name": "2029-30", "start_date": "2029-04-01", "end_date": "2030-03-31", "is_current": True}, headers=H["root"])
r = client.post("/api/school/sessions", json={"name": "2030-31", "start_date": "2030-04-01", "end_date": "2031-03-31"}, headers=H["root"])
check("a new session is added", r.status_code in (200, 201), r.get_json())
with app.app_context():
    NEW = AcademicSession.query.filter_by(name="2030-31").first().id
    CURRENT = AcademicSession.query.filter_by(is_current=True).first()
    CURRENT_ID = CURRENT.id if CURRENT else None
    CURRENT_NAME = CURRENT.name if CURRENT else None
r = client.put(f"/api/school/sessions/{NEW}", json={"end_date": "2030-01-01"}, headers=H["root"])
check("a session can't end before it starts", r.status_code == 400, r.get_json())
if CURRENT_NAME:
    r = client.put(f"/api/school/sessions/{NEW}", json={"name": CURRENT_NAME}, headers=H["root"])
    check("a session can't take another session's name", r.status_code == 409, r.get_json())
r = client.put(f"/api/school/sessions/{NEW}", json={"name": "2030-2031"}, headers=H["root"])
check("a session can be renamed", r.status_code == 200, r.get_json())
r = client.put(f"/api/school/sessions/{NEW}", json={"name": "2030-2031"}, headers=H["sara"])
check("a teacher can't edit sessions", r.status_code in (401, 403))
if CURRENT_ID:
    r = client.delete(f"/api/school/sessions/{CURRENT_ID}", headers=H["root"])
    check("the current session can't be deleted", r.status_code == 409, r.get_json())
r = client.delete(f"/api/school/sessions/{NEW}", headers=H["root"])
check("an unused session is deleted", r.status_code == 200, r.get_json())


# ---------------- L2: wording
check("plural 1", plural(1, "paper") == "1 paper")
check("plural 2", plural(2, "paper") == "2 papers")
check("plural with its own word", plural(3, "diary entry", "diary entries") == "3 diary entries")

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
