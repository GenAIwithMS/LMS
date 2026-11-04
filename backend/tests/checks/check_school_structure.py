"""School structure: Classes 1-10, sections with a class incharge, subjects and chapters per class,
who teaches what in each section, sessions, and the permissions that follow from it. In-memory SQLite."""
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
from src.models import Admin, Teacher, Section, Student, Subject

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

print("--- Classes 1 to 10")
r = client.get("/api/school/classes", headers=H["root"])
classes = r.get_json()
check("Classes 1-10 exist", [c["name"] for c in classes] == [f"Class {n}" for n in range(1, 11)], [c["name"] for c in classes][:3])
CLASS_5 = classes[4]["id"]; CLASS_4 = classes[3]["id"]

print("--- Sections and class incharges")
r = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"])
check("admin adds section 5-A with Sara as incharge", r.status_code == 201, r.get_json())
A = r.get_json()["section_id"]
r = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B"}, headers=H["root"])
B = r.get_json()["section_id"]
check("a section can start without an incharge", r.status_code == 201)
r = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A"}, headers=H["root"])
check("Class 5 can't have two sections 'A'", r.status_code == 409, r.get_json())
r = client.post(f"/api/school/classes/{CLASS_4}/sections", json={"name": "A"}, headers=H["root"])
check("Class 4 can also have a section 'A'", r.status_code == 201, r.get_json())
r = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "C"}, headers=H["sara"])
check("a teacher can't change the structure", r.status_code == 403)
r = client.put(f"/api/school/sections/{B}", json={"incharge_id": OMAR}, headers=H["root"])
check("admin sets Omar as incharge of 5-B", r.status_code == 200)

print("--- A teacher leads only one section")
r = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "C", "incharge_id": SARA}, headers=H["root"])
check("Sara (incharge of 5-A) can't lead a new section 5-C", r.status_code == 409 and "already the class incharge of Class 5 - A" in r.get_json()["message"], r.get_json())
r = client.put(f"/api/school/sections/{B}", json={"incharge_id": SARA}, headers=H["root"])
check("Sara can't also become incharge of 5-B", r.status_code == 409, r.get_json())
check("5-B still has Omar", client.get(f"/api/school/sections/{B}", headers=H["root"]).get_json()["incharge_name"] == "Omar")
r = client.put(f"/api/school/sections/{B}", json={"name": "B2", "incharge_id": SARA}, headers=H["root"])
check("a refused change doesn't half-save (the name stays B)", r.status_code == 409 and client.get(f"/api/school/sections/{B}", headers=H["root"]).get_json()["name"] == "B")
r = client.put(f"/api/school/sections/{A}", json={"incharge_id": SARA}, headers=H["root"])
check("choosing Sara again for her own 5-A is fine", r.status_code == 200, r.get_json())
r = client.post("/api/add/section", json={"name": "Old C", "teacher_id": SARA}, headers=H["root"])
check("the older section route follows the same rule", r.status_code == 409, r.get_json())
client.put(f"/api/school/sections/{A}", json={"incharge_id": None}, headers=H["root"])
r = client.put(f"/api/school/sections/{B}", json={"incharge_id": SARA}, headers=H["root"])
check("after leaving 5-A, Sara can lead 5-B", r.status_code == 200, r.get_json())
# Back to the setup the rest of this script expects
client.put(f"/api/school/sections/{B}", json={"incharge_id": OMAR}, headers=H["root"])
client.put(f"/api/school/sections/{A}", json={"incharge_id": SARA}, headers=H["root"])
r = client.get("/api/get/section", headers=H["root"])
check("the section list works and shows full names", r.status_code == 200 and "Class 5 - A" in [s.get("full_name") for s in r.get_json()], r.get_json()[:1])

print("--- Syllabus: subjects and chapters per class")
SUBJECTS = {}
for name in ["English", "Urdu", "Maths", "Science", "Social Studies", "Islamiyat", "Computer", "Art"]:
    r = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": name}, headers=H["root"])
    SUBJECTS[name] = r.get_json().get("subject_id")
check("Class 5 gets its 8 subjects", all(SUBJECTS.values()) and len(SUBJECTS) == 8)
r = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"])
check("the same subject can't be added twice to a class", r.status_code == 409)
r = client.post(f"/api/school/classes/{CLASS_4}/subjects", json={"name": "Maths"}, headers=H["root"])
check("Class 4 has its own Maths", r.status_code == 201)
MATHS_4 = r.get_json()["subject_id"]
MATHS = SUBJECTS["Maths"]; SCIENCE = SUBJECTS["Science"]
for title in ["Numbers", "Fractions", "Decimals"]:
    client.post(f"/api/school/subjects/{MATHS}/chapters", json={"title": title}, headers=H["root"])
r = client.get(f"/api/school/subjects/{MATHS}/chapters", headers=H["root"])
chapters = r.get_json()["data"]
check("chapters are numbered in order", [(c["number"], c["title"]) for c in chapters] == [(1, "Numbers"), (2, "Fractions"), (3, "Decimals")], chapters)
r = client.post(f"/api/school/subjects/{MATHS}/chapters", json={"title": "Again", "number": 2}, headers=H["root"])
check("two chapters can't have the same number", r.status_code == 409)
r = client.put(f"/api/school/chapters/{chapters[2]['id']}", json={"title": "Decimals and Percentages"}, headers=H["root"])
check("a chapter can be renamed", r.status_code == 200)
r = client.get(f"/api/school/classes/{CLASS_5}", headers=H["root"])
detail = r.get_json()
check("class page shows sections and subjects with chapter counts",
      len(detail["sections"]) == 2 and len(detail["subjects"]) == 8 and any(s["name"] == "Maths" and s["chapter_count"] == 3 for s in detail["subjects"]), detail["subjects"][:2])

print("--- Who teaches what in each section")
r = client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
check("Sara teaches Maths in 5-A", r.status_code == 200, r.get_json())
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": MATHS, "teacher_id": OMAR}, headers=H["root"])
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": SCIENCE, "teacher_id": OMAR}, headers=H["root"])
r = client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS_4, "teacher_id": SARA}, headers=H["root"])
check("a Class 4 subject can't be given to a Class 5 section", r.status_code == 400, r.get_json())
r = client.get(f"/api/school/sections/{A}", headers=H["root"])
section_a = r.get_json()
teachers = {s["subject_name"]: s["teacher_name"] for s in section_a["subjects"]}
check("5-A lists every subject with its teacher (or none yet)", teachers.get("Maths") == "Sara" and teachers.get("Science") == "Omar" and teachers.get("Art") is None, teachers)

print("--- Students with their school record")
r = client.post("/api/add/student", json={"name": "Ali", "username": "ali", "email": "ali@x.com", "password": "secret1", "section_id": A,
                                          "roll_number": "1", "admission_number": "ADM-001", "guardian_name": "Khan", "guardian_phone": "0300-0000000",
                                          "date_of_birth": "2015-04-01"}, headers=H["root"])
check("student admitted into 5-A with roll and admission numbers", r.status_code == 201, r.get_json())
r = client.post("/api/add/student", json={"name": "Bilal", "username": "bilal", "email": "bilal@x.com", "password": "secret1", "section_id": B, "admission_number": "ADM-001"}, headers=H["root"])
check("admission numbers are unique", r.status_code == 400 and "Admission number" in r.get_json()["message"], r.get_json())
client.post("/api/add/student", json={"name": "Bilal", "username": "bilal", "email": "bilal@x.com", "password": "secret1", "section_id": B, "admission_number": "ADM-002"}, headers=H["root"])
with app.app_context():
    ALI = Student.query.filter_by(username="ali").first().id
    BILAL = Student.query.filter_by(username="bilal").first().id
r = client.get("/api/get/student", headers=H["root"])
ali_row = [s for s in r.get_json() if s["username"] == "ali"][0]
check("student list shows class, section and school record",
      ali_row["section_full_name"] == "Class 5 - A" and ali_row["roll_number"] == "1" and ali_row["date_of_birth"] == "2015-04-01", ali_row)

print("--- Permissions follow the teaching assignments")
H["ali"] = login("ali")
r = client.get("/api/school/my-classes", headers=H["sara"])
mine = r.get_json()
check("Sara: incharge of 5-A, teaches Maths in 5-A",
      [s["full_name"] for s in mine["incharge_of"]] == ["Class 5 - A"] and [(t["section_name"], t["subject_name"]) for t in mine["teaching"]] == [("Class 5 - A", "Maths")], mine)
check("Sara can open 5-A", client.get(f"/api/school/sections/{A}", headers=H["sara"]).status_code == 200)
check("Sara can't open 5-B (she neither leads nor teaches there)", client.get(f"/api/school/sections/{B}", headers=H["sara"]).status_code == 403)
check("Sara's students = 5-A only", [s["username"] for s in client.get("/api/get/student", headers=H["sara"]).get_json()] == ["ali"])
check("Omar's students = 5-B (incharge) and 5-A (teaches Science)", sorted(s["username"] for s in client.get("/api/get/student", headers=H["omar"]).get_json()) == ["ali", "bilal"])

def add_marks(teacher, student_id, subject_id):
    return client.post("/api/create/result", json={"student_id": student_id, "subject_id": subject_id, "total_marks": 20,
                                                   "obtained_marks": 15, "exam_type": "quiz"}, headers=H[teacher])
r = add_marks("sara", ALI, MATHS)
check("Sara enters Maths marks for Ali (5-A)", r.status_code == 201, r.get_json())
r = add_marks("sara", ALI, SCIENCE)
check("Sara can't enter Science marks (Omar teaches Science in 5-A)", r.status_code == 400, r.get_json())
r = add_marks("omar", ALI, MATHS)
check("Omar teaches Maths, but not in 5-A, so he can't enter Ali's Maths marks", r.status_code in (400, 403), r.get_json())
r = add_marks("omar", ALI, SCIENCE)
check("Omar enters Science marks for Ali", r.status_code == 201, r.get_json())
r = add_marks("omar", BILAL, MATHS)
check("Omar enters Maths marks for Bilal (5-B)", r.status_code == 201, r.get_json())
results = client.get("/api/get/result", headers=H["sara"]).get_json()
check("Sara sees only her Maths marks for 5-A", [(x["student_name"], x["subject_name"]) for x in results] == [("Ali", "Maths")], results)

r = client.get("/api/school/my-class", headers=H["ali"])
my_class = r.get_json()
check("Ali sees his class, incharge and subject teachers",
      my_class["section_name"] == "Class 5 - A" and my_class["incharge_name"] == "Sara" and {s["subject_name"]: s["teacher_name"] for s in my_class["subjects"]}.get("Science") == "Omar", my_class)
check("Ali can read his class's syllabus", client.get(f"/api/school/subjects/{MATHS}/chapters", headers=H["ali"]).status_code == 200)
check("Ali can't read another class's syllabus", client.get(f"/api/school/subjects/{MATHS_4}/chapters", headers=H["ali"]).status_code == 403)
check("Sara can read the syllabus of a subject she teaches", client.get(f"/api/school/subjects/{MATHS}/chapters", headers=H["sara"]).status_code == 200)
check("Sara can't read the syllabus of a subject she doesn't teach", client.get(f"/api/school/subjects/{SCIENCE}/chapters", headers=H["sara"]).status_code == 403)

print("--- Safe deletes")
check("a section with students can't be deleted", client.delete(f"/api/school/sections/{A}", headers=H["root"]).status_code == 409)
check("a subject with marks can't be deleted", client.delete(f"/api/school/subjects/{MATHS}", headers=H["root"]).status_code == 409)
check("an unused subject can be deleted", client.delete(f"/api/school/subjects/{SUBJECTS['Art']}", headers=H["root"]).status_code == 200)
r = client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": SCIENCE, "teacher_id": None}, headers=H["root"])
check("a subject teacher can be removed", r.status_code == 200 and add_marks("omar", ALI, SCIENCE).status_code in (400, 403))

print("--- Academic sessions")
r = client.post("/api/school/sessions", json={"name": "2026-27", "start_date": "2026-04-01", "end_date": "2027-03-31"}, headers=H["root"])
check("the first session becomes the current one", r.status_code == 201 and client.get("/api/school/sessions", headers=H["root"]).get_json()[0]["is_current"])
r = client.post("/api/school/sessions", json={"name": "2027-28", "start_date": "2027-04-01", "end_date": "2028-03-31", "is_current": True}, headers=H["root"])
sessions = client.get("/api/school/sessions", headers=H["root"]).get_json()
check("only one session is current", [s["name"] for s in sessions if s["is_current"]] == ["2027-28"], sessions)
r = client.post("/api/school/sessions", json={"name": "bad", "start_date": "2028-04-01", "end_date": "2028-01-01"}, headers=H["root"])
check("a session must end after it starts", r.status_code == 400)

print("--- Old sections without a class or incharge still work")
with app.app_context():
    db.session.add(Section(name="Old")); db.session.commit()
r = client.get("/api/get/section", headers=H["root"])
check("section list doesn't crash on a section with no incharge", r.status_code == 200, r.status_code)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
