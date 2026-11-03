"""Website route scoping, teacher-only submissions, timestamps, login expiry. In-memory SQLite."""
import io, os, sys, time, datetime, shutil
import tempfile
SP = tempfile.mkdtemp()   # throwaway folder for uploaded test files
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40, DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles
@compiles(BigInteger, "sqlite")
def _b(t, c, **kw): return "INTEGER"

from src import create_app
from src.db import db
from src.models import (Admin, Teacher, Course, Subject, Section, Student, Assignment, Result,
                        Attendance, Announcement, AssignmentSubmission, Enrollment)
import src.services.assignment_submission as submission_service
UPLOADS = os.path.join(SP, "test_uploads2"); shutil.rmtree(UPLOADS, ignore_errors=True)
submission_service.UPLOAD_FOLDER = UPLOADS

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
    ali = make(Student, "Ali", "ali", section_id=secA.id); zara = make(Student, "Zara", "zara", section_id=secB.id)
    db.session.add_all([maths, physics, ali, zara]); db.session.commit()
    hw_sara = Assignment(title="Algebra", subject_id=maths.id, teacher_id=sara.id, due_date=datetime.date(2026, 12, 1), description="d")
    hw_omar = Assignment(title="Optics", subject_id=physics.id, teacher_id=omar.id, due_date=datetime.date(2026, 12, 1), description="d")
    r_omar = Result(subject_id=physics.id, student_id=zara.id, total_marks=20, obtained_marks=18, exam_type="quiz", grade="A")
    att_omar = Attendance(student_id=zara.id, subject_id=physics.id, status="present")
    ann_omar = Announcement(id=1, title="B trip", content="c", teacher_id=omar.id, section_id=secB.id)
    ann_all = Announcement(id=2, title="Holiday", content="c", teacher_id=omar.id, section_id=None)
    enr_zara = Enrollment(student_id=zara.id, course_id=ph.id, grade="A")
    db.session.add_all([hw_sara, hw_omar, r_omar, att_omar, ann_omar, ann_all, enr_zara]); db.session.commit()
    I = dict(hw_sara=hw_sara.id, hw_omar=hw_omar.id, r_omar=r_omar.id, att_omar=att_omar.id, ali=ali.id, zara=zara.id)

def tok(u):
    return client.post("/api/login", json={"email": f"{u}@x.com", "password": "secret1"}).get_json()["token"]
T = {u: tok(u) for u in ["root", "sara", "omar", "ali", "zara"]}
def H(u): return {"Authorization": f"Bearer {T[u]}"}
def rows(r):
    d = r.get_json()
    if isinstance(d, list): return d
    return d.get("data") or d.get("assignments") or []

print("--- Timestamps")
with app.app_context():
    a1 = Announcement(id=10, title="t1", content="c", teacher_id=1); db.session.add(a1); db.session.commit()
    time.sleep(1.2)
    a2 = Announcement(id=11, title="t2", content="c", teacher_id=1); db.session.add(a2); db.session.commit()
    check("each row gets its own creation time", a2.created_at > a1.created_at, (a1.created_at, a2.created_at))
    db.session.delete(a1); db.session.delete(a2); db.session.commit()

print("--- Login expiry")
check("login lasts 30 minutes by default", app.config["JWT_ACCESS_TOKEN_EXPIRES"] == datetime.timedelta(minutes=30))

print("--- Teacher Sara on the website")
check("student dropdown = only her students", [s["name"] for s in rows(client.get("/api/get/student", headers=H("sara")))] == ["Ali"])
check("subject dropdown = only her subjects", [s["name"] for s in rows(client.get("/api/get/subjects", headers=H("sara")))] == ["Maths"])
check("section dropdown = only her sections", [s["name"] for s in rows(client.get("/api/get/section", headers=H("sara")))] == ["A"])
check("can't open Omar's student by id", client.get(f"/api/get/student?id={I['zara']}", headers=H("sara")).status_code == 403)

check("assignment list = only hers", [a["title"] for a in rows(client.get("/api/get/assignments", headers=H("sara")))] == ["Algebra"])
r = client.post("/api/create/assignments", json={"title": "X", "description": "d", "due_date": "2026-12-05", "subject_name": "Physics", "total_marks": 10}, headers=H("sara"))
check("can't create an assignment in Physics", r.status_code == 400, r.get_json())
check("can't edit Omar's assignment", client.put(f"/api/update/assignments/?id={I['hw_omar']}", json={"title": "hacked"}, headers=H("sara")).status_code == 403)
check("can't delete Omar's assignment", client.delete(f"/api/delete/assignments/?id={I['hw_omar']}", headers=H("sara")).status_code == 403)

check("results list hides Omar's results", rows(client.get("/api/get/result", headers=H("sara"))) == [])
check("can't open Omar's result", client.get(f"/api/get/result?id={I['r_omar']}", headers=H("sara")).status_code == 403)
check("can't edit Omar's result", client.put(f"/api/update/result?id={I['r_omar']}", json={"obtained_marks": 0}, headers=H("sara")).status_code == 403)
check("can't delete Omar's result", client.delete(f"/api/delete/result?id={I['r_omar']}", headers=H("sara")).status_code == 403)
r = client.post("/api/create/result", json={"subject_name": "Maths", "student_name": "Zara", "total_marks": 20, "obtained_marks": 10, "exam_type": "quiz"}, headers=H("sara"))
check("can't add a result for Omar's student", r.status_code == 400, r.get_json())
r = client.post("/api/create/result", json={"subject_name": "Maths", "student_name": "Ali", "total_marks": 20, "obtained_marks": 15, "exam_type": "quiz"}, headers=H("sara"))
check("can add a result for her student", r.status_code in (200, 201), r.get_json())

check("attendance list hides Omar's records", rows(client.get("/api/get/attendance", headers=H("sara"))) == [])
r = client.post("/api/attendance", json={"student_name": "Zara", "subject_name": "Physics", "status": "absent"}, headers=H("sara"))
check("can't mark attendance for Omar's student/subject", r.status_code == 400, r.get_json())
check("can't edit Omar's attendance", client.put(f"/api/update/attendance?id={I['att_omar']}", json={"status": "absent"}, headers=H("sara")).status_code == 403)
check("can't delete Omar's attendance", client.delete(f"/api/delete/attendance?id={I['att_omar']}", headers=H("sara")).status_code == 403)
r = client.post("/api/attendance", json={"student_name": "Ali", "subject_name": "Maths", "status": "present"}, headers=H("sara"))
check("can mark attendance for her student", r.status_code in (200, 201), r.get_json())

r = client.post("/api/create/announcement", json={"title": "Nope", "content": "c", "section_name": "B"}, headers=H("sara"))
check("can't post to Omar's section", r.status_code == 400, r.get_json())
check("can't edit Omar's announcement", client.put("/api/update/announcement?title=B trip", json={"content": "x"}, headers=H("sara")).status_code == 403)
check("can't delete Omar's announcement", client.delete("/api/delete/announcement?title=B trip", headers=H("sara")).status_code == 403)
r = client.post("/api/create/announcement", json={"title": "Test A", "content": "c", "section_name": "A"}, headers=H("sara"))
check("can post to her own section", r.status_code in (200, 201), r.get_json())

print("--- Students")
titles = sorted(a["title"] for a in rows(client.get("/api/get/announcements", headers=H("ali"))))
check("Ali sees section A + school-wide only", titles == ["Holiday", "Test A"], titles)
check("Ali can't open section B's announcement", client.get("/api/get/announcements?title=B trip", headers=H("ali")).status_code == 404)
r = client.get("/api/get/enrollments", headers=H("ali"))
check("Ali doesn't see Zara's enrollment", rows(r) == [] or all(e.get("student_name") != "Zara" for e in rows(r)), r.get_json())
check("teacher can't list all enrollments", client.get("/api/get/enrollments", headers=H("sara")).status_code == 403)
check("admin still sees enrollments", client.get("/api/get/enrollments", headers=H("root")).status_code == 200)
check("admin still sees all results", len(rows(client.get("/api/get/result", headers=H("root")))) == 2)

print("--- Submissions: teacher's job, not the admin's")
r = client.post("/api/submit/assignment", data={"assignment_id": str(I["hw_sara"]), "submission_text": "my work", "submission_file": (io.BytesIO(b"%PDF ali"), "work.pdf")}, headers=H("ali"), content_type="multipart/form-data")
check("student submits", r.status_code == 201, r.get_json())
with app.app_context():
    sub_id = AssignmentSubmission.query.first().id
r = client.get(f"/api/get/submissions/by/assignment?id={I['hw_sara']}", headers=H("sara"))
check("Sara sees submissions to her assignment", r.status_code == 200 and len(rows(r)) == 1, r.get_json())
check("Sara downloads the file", client.get(f"/api/submission/file?id={sub_id}", headers=H("sara")).data == b"%PDF ali")
check("Sara sees Ali's submissions by student", len(rows(client.get(f"/api/get/submissions/by/student?id={I['ali']}", headers=H("sara")))) == 1)
check("Omar sees none of Ali's submissions to Sara's work", rows(client.get(f"/api/get/submissions/by/student?id={I['ali']}", headers=H("omar"))) == [])
check("admin can't list submissions", client.get(f"/api/get/submissions/by/assignment?id={I['hw_sara']}", headers=H("root")).status_code == 403)
check("admin can't view a student's submissions", client.get(f"/api/get/submissions/by/student?id={I['ali']}", headers=H("root")).status_code == 403)
check("admin can't download files", client.get(f"/api/submission/file?id={sub_id}", headers=H("root")).status_code == 403)
check("admin can't delete submissions", client.delete(f"/api/delete/submission?id={sub_id}", headers=H("root")).status_code == 403)
check("student still sees own submissions", len(rows(client.get("/api/get/submissions/by/student", headers=H("ali")))) == 1)
check("Sara grades it", client.put(f"/api/update/submission?id={sub_id}", json={"marks_obtained": "9", "feedback": "ok"}, headers=H("sara")).status_code == 200)

shutil.rmtree(UPLOADS, ignore_errors=True)
print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
