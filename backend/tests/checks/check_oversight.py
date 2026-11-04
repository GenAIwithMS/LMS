"""Admin oversight (Phase 4): the activity log and its filters, each teacher's activity,
the oversight dashboard, and the Excel reports. In-memory SQLite."""
import os, sys, io
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from datetime import timedelta
from openpyxl import load_workbook
from src import create_app
from src.db import db, pakistan_time
from src.models import Admin, Teacher, Student, ActivityLog

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
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara Ahmed", "sara"), make(Teacher, "Omar Malik", "omar")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id
    OMAR = Teacher.query.filter_by(username="omar").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root")}

TODAY = pakistan_time().date()
def day(offset):
    return (TODAY + timedelta(days=offset)).isoformat()

# School: 5-A (incharge Sara, she teaches Maths), 5-B (incharge Omar, he teaches Maths)
CLASS_5 = client.get("/api/school/classes", headers=H["root"]).get_json()[4]["id"]
client.post("/api/school/sessions", json={"name": "2026-27", "start_date": day(-100), "end_date": day(200)}, headers=H["root"])
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
B = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B", "incharge_id": OMAR}, headers=H["root"]).get_json()["section_id"]
MATHS = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"]).get_json()["subject_id"]
CHAPTERS = []
for title in ["Numbers", "Fractions", "Decimals", "Geometry"]:
    CHAPTERS.append(client.post(f"/api/school/subjects/{MATHS}/chapters", json={"title": title}, headers=H["root"]).get_json()["chapter"]["id"])
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": MATHS, "teacher_id": OMAR}, headers=H["root"])
for name, uname, section, roll in [("Ali", "ali", A, "1"), ("Hina", "hina", A, "2"), ("Bilal", "bilal", B, "1")]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1",
                                          "section_id": section, "roll_number": roll}, headers=H["root"])
with app.app_context():
    ALI = Student.query.filter_by(username="ali").first().id
    HINA = Student.query.filter_by(username="hina").first().id
term = client.post("/api/exams/terms", json={"session_id": 1, "name": "First Term", "start_date": day(-5), "end_date": day(5)}, headers=H["root"]).get_json()["term"]["id"]
client.post(f"/api/exams/terms/{term}/papers", json={"class_id": CLASS_5}, headers=H["root"])

print("--- Activity log: what gets written")
client.post("/api/login", json={"email": "sara@x.com", "password": "wrong-password"})
H["sara"] = login("sara")
H["omar"] = login("omar")
client.post(f"/api/school/sections/{A}/attendance", json={"date": day(0), "records": [{"student_id": ALI, "status": "present"}, {"student_id": HINA, "status": "absent"}]}, headers=H["sara"])
client.post(f"/api/school/sections/{A}/attendance", json={"date": day(-1), "records": [{"student_id": ALI, "status": "present"}, {"student_id": HINA, "status": "absent"}]}, headers=H["sara"])
client.post(f"/api/school/sections/{A}/diary", json={"subject_id": MATHS, "date": day(0), "homework": "Ex 1"}, headers=H["sara"])
client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[0]}/progress", json={"status": "done"}, headers=H["sara"])
client.put(f"/api/school/sections/{A}/chapters/{CHAPTERS[1]}/progress", json={"status": "done"}, headers=H["sara"])
client.post("/api/create/assignments", json={"title": "Worksheet", "description": "Do it", "due_date": day(3), "subject_id": MATHS}, headers=H["sara"])
client.post(f"/api/school/sections/{B}/attendance", json={"date": day(0), "records": [{"student_id": ALI, "status": "present"}]}, headers=H["sara"])   # refused (403)
client.get("/api/school/my-classes", headers=H["sara"])          # just looking: not logged
client.post("/api/logout", headers=H["omar"])

r = client.get("/api/oversight/activity?per_page=200", headers=H["root"])
log = r.get_json()["entries"]
descriptions = [e["description"] for e in log]
check("the admin reads the log, newest first", r.status_code == 200 and log[0]["description"] == "Logged out" and log[0]["user_name"] == "Omar Malik", log[:2])
sara_login = [e for e in log if e["action"] == "login" and e["user_name"] == "Sara Ahmed"]
check("logins are logged with the person and IP", len(sara_login) == 1 and sara_login[0]["user_id"] == SARA and sara_login[0]["ip_address"], sara_login)
failed = [e for e in log if e["action"] == "login_failed"]
check("a failed login is logged with the email tried", len(failed) == 1 and failed[0]["user_name"] == "sara@x.com" and failed[0]["user_id"] is None, failed)
check("attendance is logged with the section", "Marked daily attendance: Class 5 - A" in descriptions, descriptions[:8])
check("the diary is logged with subject and section", "Wrote the diary: Maths, Class 5 - A" in descriptions)
check("a refused request is not logged", len([e for e in log if e["user_name"] == "Sara Ahmed" and "Class 5 - B" in e["description"]]) == 0)
check("just looking at pages is not logged", not any("my-classes" in d for d in descriptions))
with app.app_context():
    stored = " ".join(e.description + e.path for e in ActivityLog.query.all())
check("no password is ever stored", "secret1" not in stored and "wrong-password" not in stored)

print("--- Activity log: filters")
def search(query):
    return client.get("/api/oversight/activity?" + query, headers=H["root"]).get_json()["entries"]
by_name = search("name=sar")
check("filter by teacher name (part of it)", len(by_name) > 0 and all(e["user_name"] in ("Sara Ahmed", "sara@x.com") for e in by_name), set(e["user_name"] for e in by_name))
check("filter by action", all(e["action"] == "login" for e in search("action=login")) and len(search("action=login")) == 3)
check("filter by area", [e["description"] for e in search("area=diary")] == ["Wrote the diary: Maths, Class 5 - A"])
check("filter by class", len(search(f"class_id={CLASS_5}&name=Sara")) >= 4)
check("filter by section", all(e["section_id"] == A for e in search(f"section_id={A}")))
check("filter by date: today has entries, yesterday has none", len(search(f"date_from={day(0)}")) > 0 and search(f"date_to={day(-1)}") == [])
check("a bad date is refused", client.get("/api/oversight/activity?date_from=yesterday", headers=H["root"]).status_code == 400)
paged = client.get("/api/oversight/activity?per_page=2&page=2", headers=H["root"]).get_json()
check("the log is paged", len(paged["entries"]) == 2 and paged["page"] == 2 and paged["total"] > 4, paged["total"])
check("the area list is there for the filter", "attendance" in client.get("/api/oversight/activity/areas", headers=H["root"]).get_json())
check("teachers can't read the log", client.get("/api/oversight/activity", headers=H["sara"]).status_code == 403)

print("--- Teachers' activity")
overview = client.get("/api/oversight/teachers", headers=H["root"]).get_json()
rows = {t["name"]: t for t in overview["teachers"]}
sara = rows["Sara Ahmed"]
check("Sara this week: 2 attendance days, 1 diary entry, 1 assignment, 2 syllabus updates",
      sara["this_week"]["attendance_days_marked"] == 2 and sara["this_week"]["diary_entries"] == 1 and sara["this_week"]["assignments"] == 1
      and sara["this_week"]["progress_updates"] == 2, sara["this_week"])
check("Sara's last login is shown", sara["last_login"] is not None)
check("Omar hasn't marked 5-B today; Sara has marked 5-A", rows["Omar Malik"]["attendance_not_marked_today"] == ["Class 5 - B"] and sara["attendance_not_marked_today"] == [], rows["Omar Malik"])
check("both have marks missing in the open term", sara["papers_pending"] == 1 and rows["Omar Malik"]["papers_pending"] == 1)
detail = client.get(f"/api/oversight/teachers/{SARA}", headers=H["root"]).get_json()
check("Sara's page: Maths in 5-A, 2 of 4 chapters (50%)",
      [(t["section_name"], t["subject_name"], t["chapters_done"], t["chapter_count"], t["percentage"]) for t in detail["teaching"]] == [("Class 5 - A", "Maths", 2, 4, 50)], detail["teaching"])
check("her diary and assignments this week", len(detail["diary_this_week"]) == 1 and detail["assignments_this_week"][0]["title"] == "Worksheet")
check("marks still to enter", detail["marks_pending"] == [{"term_name": "First Term", "subject_name": "Maths", "section_name": "Class 5 - A", "entered": 0, "student_count": 2}], detail["marks_pending"])
check("her recent actions", any(a["description"].startswith("Updated syllabus progress") for a in detail["recent_actions"]))
check("an unknown teacher gives 404", client.get("/api/oversight/teachers/9999", headers=H["root"]).status_code == 404)

print("--- Oversight dashboard")
dash = client.get("/api/oversight/dashboard", headers=H["root"]).get_json()
check("1 of 2 sections marked today", dash["counts"]["sections"] == 2 and dash["counts"]["sections_marked_today"] == 1, dash["counts"])
row_a = [s for s in dash["attendance_today"] if s["section_name"] == "Class 5 - A"][0]
check("today's numbers for 5-A", row_a["present"] == 1 and row_a["absent"] == 1 and row_a["is_marked"], row_a)
coverage = dash["syllabus_coverage"][0]
check("syllabus coverage: 5-A 50%, 5-B 0%, Class 5 average 25%",
      [s["average_percentage"] for s in coverage["sections"]] == [50, 0] and coverage["average_percentage"] == 25, coverage)
check("marks pending for each section", sorted(m["section_name"] for m in dash["marks_pending"]) == ["Class 5 - A", "Class 5 - B"])
check("Hina (0%) is on the low attendance list, Ali isn't", [s["name"] for s in dash["low_attendance"]] == ["Hina"], dash["low_attendance"])
check("teachers can't open the dashboard", client.get("/api/oversight/dashboard", headers=H["sara"]).status_code == 403)

print("--- Excel reports")
def report(query):
    return client.get("/api/reports/" + query, headers=H["root"])
def sheet_text(response):
    workbook = load_workbook(io.BytesIO(response.data))
    values = []
    for row in workbook.active.iter_rows(values_only=True):
        for value in row:
            if value is not None:
                values.append(str(value))
    return values
r = report(f"attendance?section_id={A}&month={day(0)[:7]}")
check("attendance report is an Excel file", r.status_code == 200 and "spreadsheetml" in r.content_type and r.data[:2] == b"PK", r.content_type)
check("with each student's days", "Hina" in sheet_text(r) and "Attendance %" in sheet_text(r))
r = report(f"results?term_id={term}&section_id={A}")
check("results report", r.status_code == 200 and "Maths (100)" in sheet_text(r) and "Incomplete" in sheet_text(r), sheet_text(r)[:12])
check("syllabus report", "Fractions" not in sheet_text(report("syllabus")) and "Covered %" in sheet_text(report("syllabus")))
check("teacher activity report", "Sara Ahmed" in sheet_text(report("teachers")))
check("low attendance report", "Hina" in sheet_text(report("low-attendance")))
check("activity log report, with filters", "Wrote the diary: Maths, Class 5 - A" in sheet_text(report("activity?area=diary")))
check("attendance report needs a section", report("attendance").status_code == 400)
check("an unknown report gives 404", report("salaries").status_code == 404)
check("teachers can't download reports", client.get("/api/reports/teachers", headers=H["sara"]).status_code == 403)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
