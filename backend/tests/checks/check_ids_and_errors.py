"""Forms pick teachers, courses, sections and subjects by ID; JSON for every error; password change rate limit."""
import os, sys, datetime
os.environ.update(RATELIMIT_ENABLED="true", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from school_setup import give_teachers_their_subjects, make_every_day_a_school_day
from src import create_app
from src.db import db
from src.models import Admin, Teacher, Course, Subject, Section, Student, Result, Attendance, Assignment, Enrollment, Announcement
import src.routes.course as course_route

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
    admin = make(Admin, "Root", "root")
    ali_1 = make(Teacher, "Ali", "ali.t1"); ali_2 = make(Teacher, "Ali", "ali.t2"); omar = make(Teacher, "Omar", "omar")
    db.session.add_all([admin, ali_1, ali_2, omar]); db.session.commit()
    cs = Course(name="CS", course_code="CS1", teacher_id=ali_1.id); se = Course(name="SE", course_code="SE1", teacher_id=ali_1.id)
    sec_a = Section(name="A", teacher_id=ali_1.id); sec_a2 = Section(name="A", teacher_id=omar.id)
    db.session.add_all([cs, se, sec_a, sec_a2]); db.session.commit()
    # Teacher ali.t1 teaches "Maths" in two courses
    maths_cs = Subject(name="Maths", teacher_id=ali_1.id, course_id=cs.id)
    maths_se = Subject(name="Maths", teacher_id=ali_1.id, course_id=se.id)
    physics = Subject(name="Physics", teacher_id=omar.id, course_id=cs.id)
    student = make(Student, "Zain", "zain", section_id=sec_a.id)
    db.session.add_all([maths_cs, maths_se, physics, student]); db.session.commit()
    give_teachers_their_subjects()
    I = dict(ali_1=ali_1.id, ali_2=ali_2.id, cs=cs.id, se=se.id, sec_a=sec_a.id, sec_a2=sec_a2.id,
             maths_cs=maths_cs.id, maths_se=maths_se.id, physics=physics.id, zain=student.id)

def headers(user, ip="10.0.0.1"):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"},
                        environ_base={"REMOTE_ADDR": ip}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": headers("root"), "ali.t1": headers("ali.t1", ip="10.0.0.2")}

print("--- Admin forms pick by ID (two teachers are called Ali)")
r = client.post("/api/add/course", json={"name": "AI", "description": "d", "course_code": "AI1", "teacher_id": I["ali_2"]}, headers=H["root"])
with app.app_context():
    course = Course.query.filter_by(name="AI").first()
    check("course goes to the second Ali when his ID is sent", r.status_code in (200, 201) and course and course.teacher_id == I["ali_2"], r.get_json())
    AI = course.id
r = client.put(f"/api/update/course?id={AI}", json={"teacher_id": I["ali_1"]}, headers=H["root"])
with app.app_context():
    check("course teacher can be changed by ID", Course.query.get(AI).teacher_id == I["ali_1"], r.get_json())
r = client.post("/api/create/subject", json={"name": "Stats", "teacher_id": I["ali_2"], "course_id": I["se"]}, headers=H["root"])
with app.app_context():
    stats = Subject.query.filter_by(name="Stats").first()
    check("subject gets the teacher and course by ID", stats and stats.teacher_id == I["ali_2"] and stats.course_id == I["se"], r.get_json())
r = client.post("/api/add/section", json={"name": "B", "teacher_id": I["ali_2"]}, headers=H["root"])
with app.app_context():
    section_b = Section.query.filter_by(name="B").first()
    check("section gets the teacher by ID", section_b and section_b.teacher_id == I["ali_2"], r.get_json())
r = client.post("/api/add/student", json={"name": "Sana", "username": "sana", "email": "sana@x.com", "password": "secret1", "section_id": I["sec_a2"]}, headers=H["root"])
with app.app_context():
    sana = Student.query.filter_by(username="sana").first()
    check("student goes into the second section 'A' by ID", sana and sana.section_id == I["sec_a2"], r.get_json())
r = client.post("/api/enroll/student", json={"student_id": I["zain"], "course_id": I["se"], "status": "active"}, headers=H["root"])
with app.app_context():
    check("enrollment gets the course by ID", Enrollment.query.filter_by(student_id=I["zain"], course_id=I["se"]).first() is not None, r.get_json())
r = client.post("/api/add/course", json={"name": "X", "description": "d", "course_code": "X1"}, headers=H["root"])
check("no teacher at all -> clear 400", r.status_code == 400 and r.get_json()["message"] == "Teacher not found", r.get_json())
r = client.post("/api/add/course", json={"name": "Y", "description": "d", "course_code": "Y1", "teacher_name": "Omar"}, headers=H["root"])
check("a name still works (chatbot, older requests)", r.status_code in (200, 201), r.get_json())

print("--- Teacher forms pick by ID (ali.t1 teaches Maths in two courses)")
T = H["ali.t1"]
r = client.post("/api/attendance", json={"student_id": I["zain"], "subject_id": I["maths_se"], "status": "present"}, headers=T)
with app.app_context():
    check("attendance goes to Maths in SE when its ID is sent", Attendance.query.filter_by(subject_id=I["maths_se"]).count() == 1, r.get_json())
r = client.post("/api/attendance", json={"student_id": I["zain"], "subject_id": I["physics"], "status": "present"}, headers=T)
check("ID of another teacher's subject is refused", r.status_code == 400, r.get_json())
r = client.post("/api/create/result", json={"student_id": I["zain"], "subject_id": I["maths_se"], "total_marks": 20, "obtained_marks": 15, "exam_type": "quiz"}, headers=T)
with app.app_context():
    result = Result.query.filter_by(subject_id=I["maths_se"]).first()
    check("result goes to Maths in SE by ID", result is not None, r.get_json())
    RESULT = result.id
r = client.put(f"/api/update/result?id={RESULT}", json={"subject_id": I["physics"]}, headers=T)
with app.app_context():
    check("an update can't move a result into another teacher's subject", r.status_code == 400 and Result.query.get(RESULT).subject_id == I["maths_se"], r.get_json())
r = client.post("/api/create/assignments", json={"title": "HW", "description": "d", "due_date": str(datetime.date.today() + datetime.timedelta(days=5)), "total_marks": 10, "subject_id": I["maths_se"]}, headers=T)
with app.app_context():
    hw = Assignment.query.filter_by(title="HW").first()
    check("assignment goes to Maths in SE by ID", hw and hw.subject_id == I["maths_se"], r.get_json())
    HW = hw.id
r = client.put(f"/api/update/assignments/?id={HW}", json={"subject_id": I["physics"]}, headers=T)
with app.app_context():
    check("an update can't move an assignment into another teacher's subject", r.status_code == 400 and Assignment.query.get(HW).subject_id == I["maths_se"], r.get_json())
r = client.post("/api/create/announcement", json={"title": "T1", "content": "c", "section_id": I["sec_a"]}, headers=T)
check("announcement to own section by ID", r.status_code in (200, 201), r.get_json())
r = client.post("/api/create/announcement", json={"title": "T2", "content": "c", "section_id": I["sec_a2"]}, headers=T)
check("ID of another teacher's section 'A' is refused", r.status_code == 400, r.get_json())

print("--- Every error is JSON")
r = client.get("/api/this/does/not/exist", headers=H["root"])
check("unknown address -> JSON 404", r.status_code == 404 and r.is_json and r.get_json()["status"] == "failed", r.get_data(as_text=True)[:80])
r = client.delete("/api/login")
check("wrong method -> JSON 405", r.status_code == 405 and r.is_json, r.get_data(as_text=True)[:80])
def crash():
    raise RuntimeError("secret internal detail")
course_route.get_all_courses = crash
r = client.get("/api/get/courses", headers=H["root"])
body = r.get_data(as_text=True)
check("unexpected crash -> JSON 500 with a plain message", r.status_code == 500 and r.is_json and "Something went wrong" in body, body[:80])
check("unexpected crash -> no internal details sent", "secret internal detail" not in body and "Traceback" not in body)
r = client.get("/api/get/student", headers=H["root"])
check("the server keeps working after a crash", r.status_code == 200)
r = client.get("/api/get/student")
check("missing login still gets the login error, not the catch-all", r.status_code == 401, r.get_json())

print("--- Password change is rate limited")
codes = []
for attempt in range(7):
    codes.append(client.put("/api/account/password", json={"current_password": "wrongpass", "new_password": "another1"}, headers=T).status_code)
check("6th wrong current password in a minute -> 429", codes[:5] == [400] * 5 and codes[5] == 429, codes)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
