"""No duplicate enrollments, attendance, exam results or submissions; due dates; enrollment date; announcement titles."""
import io, os, sys, datetime, tempfile
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from school_setup import give_teachers_their_subjects
from src import create_app
from src.db import db
from src.models import Admin, Teacher, Course, Subject, Section, Student, Assignment, AssignmentSubmission, Enrollment, Announcement
import src.services.assignment_submission as submission_service

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

today = datetime.date.today()
with app.app_context():
    db.create_all()
    admin = make(Admin, "Root", "root"); sara = make(Teacher, "Sara", "sara")
    db.session.add_all([admin, sara]); db.session.commit()
    course = Course(name="CS", course_code="CS1", teacher_id=sara.id); sec = Section(name="A", teacher_id=sara.id)
    db.session.add_all([course, sec]); db.session.commit()
    maths = Subject(name="Maths", teacher_id=sara.id, course_id=course.id)
    ali = make(Student, "Ali", "ali", section_id=sec.id)
    db.session.add_all([maths, ali]); db.session.commit()
    open_hw = Assignment(title="Open", subject_id=maths.id, teacher_id=sara.id, due_date=today + datetime.timedelta(days=7), description="d")
    due_today = Assignment(title="Due today", subject_id=maths.id, teacher_id=sara.id, due_date=today, description="d")
    closed_hw = Assignment(title="Closed", subject_id=maths.id, teacher_id=sara.id, due_date=today - datetime.timedelta(days=1), description="d")
    db.session.add_all([open_hw, due_today, closed_hw]); db.session.commit()
    give_teachers_their_subjects()
    I = dict(ali=ali.id, open=open_hw.id, today=due_today.id, closed=closed_hw.id)

def token(user):
    return client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
H = {}
for user in ["root", "sara", "ali"]:
    H[user] = {"Authorization": f"Bearer {token(user)}"}

print("--- Enrollments")
r = client.post("/api/enroll/student", json={"student_id": I["ali"], "course_name": "CS", "status": "active"}, headers=H["root"])
check("first enrollment works", r.status_code == 201, r.get_json())
with app.app_context():
    enrollment = Enrollment.query.first()
    check("enrollment without a date gets today's date", enrollment.enrollment_date is not None and enrollment.enrollment_date.date() == today, enrollment.enrollment_date)
r = client.post("/api/enroll/student", json={"student_id": I["ali"], "course_name": "CS", "status": "active"}, headers=H["root"])
check("enrolling the same student in the same course again is refused", r.status_code == 409, r.get_json())

print("--- Attendance")
body = {"student_id": I["ali"], "subject_name": "Maths", "status": "present"}
r = client.post("/api/attendance", json=body, headers=H["sara"])
check("first attendance today works", r.status_code == 201, r.get_json())
r = client.post("/api/attendance", json=body, headers=H["sara"])
check("marking the same student again today is refused", r.status_code == 409 and "already marked" in r.get_json()["message"], r.get_json())

print("--- Results")
def add_result(exam_type):
    return client.post("/api/create/result", json={"student_id": I["ali"], "subject_name": "Maths", "total_marks": 20,
                                                   "obtained_marks": 15, "exam_type": exam_type}, headers=H["sara"])
check("first midterm works", add_result("midterm").status_code == 201)
r = add_result("midterm")
check("a second midterm in the same subject is refused", r.status_code == 409, r.get_json())
check("first quiz works", add_result("quiz").status_code == 201)
check("a second quiz is allowed (there are usually several)", add_result("quiz").status_code == 201)

print("--- Submissions")
def submit(assignment_id, text, file_bytes=None, file_name="answer.pdf"):
    data = {"assignment_id": str(assignment_id), "submission_text": text}
    if file_bytes is not None:
        data["submission_file"] = (io.BytesIO(file_bytes), file_name)
    return client.post("/api/submit/assignment", data=data, headers=H["ali"], content_type="multipart/form-data")

r = submit(I["closed"], "late work")
check("submitting after the due date is refused", r.status_code == 400 and "due date" in r.get_json()["message"], r.get_json())
r = submit(I["today"], "on the last day")
check("submitting on the due date itself is allowed", r.status_code == 201, r.get_json())
r = submit(I["open"], "first try", b"%PDF first")
check("first submission works", r.status_code == 201, r.get_json())
first_files = os.listdir(UPLOADS)
r = submit(I["open"], "second try", b"%PDF second")
check("resubmitting before the due date replaces the earlier one", r.status_code == 200 and "replaced" in r.get_json()["message"], r.get_json())
with app.app_context():
    rows = AssignmentSubmission.query.filter_by(student_id=I["ali"], assignment_id=I["open"]).all()
    check("still only one submission for that assignment", len(rows) == 1, len(rows))
    check("it holds the new text", rows[0].submission_text == "second try", rows[0].submission_text)
    sub_id = rows[0].id
files_now = os.listdir(UPLOADS)
check("the old file was removed and the new one kept", len(files_now) == 1 and files_now != first_files, (first_files, files_now))
r = client.put(f"/api/update/submission?id={sub_id}", json={"marks_obtained": "9", "feedback": "good"}, headers=H["sara"])
check("teacher grades it", r.status_code == 200, r.get_json())
r = submit(I["open"], "third try")
check("a graded submission can't be replaced", r.status_code == 409, r.get_json())

print("--- Announcement titles")
for title in ["Test", "Trip"]:
    client.post("/api/create/announcement", json={"title": title, "content": "c", "section_name": "A"}, headers=H["sara"])
r = client.put("/api/update/announcement?title=Trip", json={"title": "Test"}, headers=H["sara"])
check("renaming to another announcement's title is refused", r.status_code == 400, r.get_json())
r = client.put("/api/update/announcement?title=Trip", json={"title": "School trip"}, headers=H["sara"])
check("renaming to a free title works", r.status_code == 200, r.get_json())
with app.app_context():
    check("titles stay unique", sorted(a.title for a in Announcement.query.all()) == ["School trip", "Test"])

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
