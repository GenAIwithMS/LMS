"""Crash fixes, student assignment scoping, ID-based student selection. In-memory SQLite."""
import os, sys, datetime
import tempfile
SP = tempfile.mkdtemp()   # throwaway folder for uploaded test files
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40, DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder
from sqlalchemy import BigInteger, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.compiler import compiles
@compiles(BigInteger, "sqlite")
def _b(t, c, **kw): return "INTEGER"
@event.listens_for(Engine, "connect")
def _fk(conn, rec):          # make SQLite enforce foreign keys like MySQL does
    conn.execute("PRAGMA foreign_keys=ON")

from src import create_app
from src.db import db
from src.models import Admin, Teacher, Course, Subject, Section, Student, Assignment, Attendance, Result, Enrollment

app = create_app(); client = app.test_client(); fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond: fails.append(name)
def make(cls, name, uname, **kw):
    u = cls(name=name, username=uname, email=f"{uname}@x.com", **kw); u.set_password("secret1"); return u

with app.app_context():
    db.create_all()
    admin = make(Admin, "Root", "root"); sara = make(Teacher, "Sara", "sara"); omar = make(Teacher, "Omar", "omar")
    db.session.add_all([admin, sara, omar]); db.session.commit()
    cs = Course(name="CS", course_code="CS1", teacher_id=sara.id); ph = Course(name="PH", course_code="PH1", teacher_id=omar.id)
    secA = Section(name="A", teacher_id=sara.id); secB = Section(name="B", teacher_id=omar.id)
    db.session.add_all([cs, ph, secA, secB]); db.session.commit()
    maths = Subject(name="Maths", teacher_id=sara.id, course_id=cs.id); physics = Subject(name="Physics", teacher_id=omar.id, course_id=ph.id)
    ali1 = make(Student, "Ali", "ali.khan", section_id=secA.id); ali2 = make(Student, "Ali", "ali.raza", section_id=secA.id)
    zara = make(Student, "Zara", "zara", section_id=secB.id)
    db.session.add_all([maths, physics, ali1, ali2, zara]); db.session.commit()
    hw_sara = Assignment(title="Algebra", subject_id=maths.id, teacher_id=sara.id, due_date=datetime.date(2026, 12, 1), description="d")
    hw_omar = Assignment(title="Optics", subject_id=physics.id, teacher_id=omar.id, due_date=datetime.date(2026, 12, 1), description="d")
    db.session.add_all([hw_sara, hw_omar]); db.session.commit()
    db.session.add(Attendance(student_id=zara.id, subject_id=physics.id, status="present")); db.session.commit()
    I = dict(ali1=ali1.id, ali2=ali2.id, zara=zara.id, hw_sara=hw_sara.id, hw_omar=hw_omar.id, secB=secB.id, maths=maths.id)

def tok(u): return client.post("/api/login", json={"email": f"{u}@x.com", "password": "secret1"}).get_json()["token"]
T = {u: tok(u) for u in ["root", "sara", "ali.khan", "zara"]}
def H(u): return {"Authorization": f"Bearer {T[u]}"}
def rows(r):
    d = r.get_json()
    return d if isinstance(d, list) else (d.get("data") or d.get("assignments") or [])

print("--- Results: bad values give 400, not a crash")
def add_result(**kw):
    body = {"student_id": I["ali1"], "subject_name": "Maths", "total_marks": 20, "obtained_marks": 10, "exam_type": "quiz"}
    body.update(kw)
    return client.post("/api/create/result", json=body, headers=H("sara"))
r = add_result(total_marks=0); check("total marks 0 -> 400", r.status_code == 400, r.get_json())
r = add_result(obtained_marks=25); check("obtained > total -> 400", r.status_code == 400, r.get_json())
r = add_result(obtained_marks=-1); check("negative marks -> 400", r.status_code == 400, r.get_json())
r = add_result(exam_type="weekly"); check("unknown exam type -> 400", r.status_code == 400, r.get_json())
r = add_result(); check("valid result saved", r.status_code == 201, r.get_json())
with app.app_context():
    res = Result.query.first(); RES = res.id
    check("grade is a letter", res.grade == "F", res.grade)
    check("result went to the chosen Ali (by ID)", res.student_id == I["ali1"])
r = client.put(f"/api/update/result?id={RES}", json={"obtained_marks": 50}, headers=H("sara"))
check("update to obtained > total -> 400", r.status_code == 400, r.get_json())
r = client.put(f"/api/update/result?id={RES}", json={"student_id": I["ali1"], "student_name": "Ali", "obtained_marks": 18, "remarks": "good"}, headers=H("sara"))
check("edit form sending student_id works", r.status_code == 200, r.get_json())

print("--- Deletes that other records need give 409, not a crash")
r = client.delete(f"/api/delete/section?id={I['secB']}", headers=H("root"))
check("delete section with students -> 409 with message", r.status_code == 409 and "students" in r.get_json()["message"], r.get_json())
r = client.delete(f"/api/delete/student?id={I['zara']}", headers=H("root"))
check("delete student with attendance -> 409", r.status_code == 409, r.get_json())
r = client.get("/api/get/student", headers=H("root"))
check("database still works after the refused delete", r.status_code == 200)
r = client.delete("/api/delete/enrollment?id=999", headers=H("root"))
check("deleting a missing enrollment -> 404, not a crash", r.status_code == 404, r.status_code)
r = client.get("/api/get/admin?id=1", headers=H("root"))
check("get admin by id works", r.status_code == 200 and r.get_json()["username"] == "root", r.get_json())

print("--- Students only see assignments from their own teachers")
titles = [a["title"] for a in rows(client.get("/api/get/assignments", headers=H("ali.khan")))]
check("Ali sees Sara's assignment only", titles == ["Algebra"], titles)
titles = [a["title"] for a in rows(client.get("/api/get/assignments", headers=H("zara")))]
check("Zara sees Omar's assignment only", titles == ["Optics"], titles)
r = client.get(f"/api/get/assignments?id={I['hw_omar']}", headers=H("ali.khan"))
check("Ali can't open Omar's assignment", r.status_code == 404)
r = client.post("/api/submit/assignment", data={"assignment_id": str(I["hw_omar"]), "submission_text": "x"}, headers=H("ali.khan"), content_type="multipart/form-data")
check("Ali can't submit to Omar's assignment", r.status_code == 404, r.get_json())
r = client.post("/api/submit/assignment", data={"assignment_id": str(I["hw_sara"]), "submission_text": "x"}, headers=H("ali.khan"), content_type="multipart/form-data")
check("Ali submits to Sara's assignment", r.status_code == 201, r.get_json())

print("--- Forms pick students by ID")
r = client.post("/api/attendance", json={"student_id": I["ali2"], "student_name": "Ali", "subject_name": "Maths", "status": "late"}, headers=H("sara"))
check("attendance by ID", r.status_code in (200, 201), r.get_json())
with app.app_context():
    check("attendance went to the second Ali", Attendance.query.filter_by(student_id=I["ali2"]).count() == 1)
r = client.post("/api/attendance", json={"student_id": I["zara"], "subject_name": "Maths", "status": "late"}, headers=H("sara"))
check("ID of another teacher's student is refused", r.status_code == 400, r.get_json())
r = client.get("/api/get/attendance", headers=H("sara"))
check("attendance list includes student_id", all("student_id" in a for a in rows(r)), rows(r)[:1])
with app.app_context():
    att = Attendance.query.filter_by(student_id=I["ali2"]).first().id
r = client.put(f"/api/update/attendance?id={att}", json={"student_id": I["ali1"], "student_name": "Ali", "subject_name": "Maths", "status": "present"}, headers=H("sara"))
check("attendance edit by ID", r.status_code == 200, r.get_json())
with app.app_context():
    check("edit moved it to the first Ali", Attendance.query.get(att).student_id == I["ali1"])
r = client.post("/api/enroll/student", json={"student_id": I["ali2"], "student_name": "Ali", "course_name": "CS", "status": "active"}, headers=H("root"))
check("enrollment by ID", r.status_code in (200, 201), r.get_json())
with app.app_context():
    enr = Enrollment.query.filter_by(student_id=I["ali2"]).first()
    check("enrolled the second Ali", enr is not None)
r = client.put(f"/api/update/enrollment?id={enr.id}", json={"student_id": I["ali2"], "student_name": "Ali", "course_name": "CS", "status": "completed", "grade": "A"}, headers=H("root"))
check("enrollment edit form (with student_id) works", r.status_code == 200, r.get_json())
r = client.post("/api/attendance", json={"student_name": "Bilal", "subject_name": "Maths", "status": "late"}, headers=H("sara"))
check("old name-based requests still work (unknown name -> 400)", r.status_code == 400)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
