"""No raw error text sent to the browser; empty lists are not "not found"; no relationship warnings. In-memory SQLite."""
import os, sys, types, warnings
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
from src.models import Admin, Teacher, Course, Subject, Section, Student, Assignment
import src.routes.assignment_submission as submission_route
import src.services.assignment_submission as submission_service
import datetime

fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond:
        fails.append(name)

print("--- No relationship warnings")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    app = create_app()
    with app.app_context():
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
relationship_warnings = [str(w.message) for w in caught if "relationship" in str(w.message).lower()]
check("Student.courses and Enrollment no longer overlap", relationship_warnings == [], relationship_warnings[:1])

client = app.test_client()

def make(cls, name, uname, **kw):
    u = cls(name=name, username=uname, email=f"{uname}@x.com", **kw); u.set_password("secret1"); return u

with app.app_context():
    db.create_all()
    admin = make(Admin, "Root", "root"); sara = make(Teacher, "Sara", "sara")
    db.session.add_all([admin, sara]); db.session.commit()
    course = Course(name="CS", course_code="CS1", teacher_id=sara.id); sec = Section(name="A", teacher_id=sara.id)
    db.session.add_all([course, sec]); db.session.commit()
    maths = Subject(name="Maths", teacher_id=sara.id, course_id=course.id)
    db.session.add(maths); db.session.commit()
    hw = Assignment(title="HW", subject_id=maths.id, teacher_id=sara.id,
                    due_date=datetime.date.today() + datetime.timedelta(days=7), description="d")
    db.session.add(hw); db.session.commit()
    HW = hw.id; MATHS = maths.id

def headers(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": headers("root"), "sara": headers("sara")}

print("--- Empty lists are not 'not found'")
r = client.get("/api/get/student", headers=H["root"])
check("no students yet -> 200 and an empty list", r.status_code == 200 and r.get_json() == [], (r.status_code, r.get_json()))
r = client.get("/api/get/attendance?subject_name=Maths", headers=H["root"])
check("no attendance for a subject -> 200 and an empty list", r.status_code == 200 and r.get_json() == [], (r.status_code, r.get_json()))
with app.app_context():
    ali = make(Student, "Ali", "ali", section_id=1); db.session.add(ali); db.session.commit()   # section A has id 1
r = client.get("/api/get/attendance?student_name=Ali", headers=H["root"])
check("a student with no attendance -> 200 and an empty list", r.status_code == 200 and r.get_json() == [], (r.status_code, r.get_json()))

print("--- No raw error text sent to the browser")
original_route_function = submission_route.get_submissions_by_assignment
def broken(*args, **kwargs):
    raise RuntimeError("secret internal detail")
submission_route.get_submissions_by_assignment = broken
r = client.get(f"/api/get/submissions/by/assignment?id={HW}", headers=H["sara"])
body = r.get_data(as_text=True)
check("route error: 500 with a plain message", r.status_code == 500 and "Could not load the submissions" in body, body[:100])
check("route error: the internal detail is not sent", "secret internal detail" not in body)
submission_route.get_submissions_by_assignment = original_route_function

def raise_error(**kwargs):
    raise RuntimeError("secret database detail")
original_model = submission_service.AssignmentSubmission
submission_service.AssignmentSubmission = types.SimpleNamespace(query=types.SimpleNamespace(filter_by=raise_error))
r = client.get(f"/api/get/submissions/by/assignment?id={HW}", headers=H["sara"])
body = r.get_data(as_text=True)
check("service error: plain message, internal detail not sent",
      r.status_code == 500 and "Could not load the submissions" in body and "secret database detail" not in body, body[:100])
submission_service.AssignmentSubmission = original_model

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
