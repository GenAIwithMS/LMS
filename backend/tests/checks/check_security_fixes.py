"""Tests for the critical security fixes. In-memory SQLite, no LLM calls."""
import io, os, sys, datetime, shutil
import tempfile
SP = tempfile.mkdtemp()   # throwaway folder for uploaded test files
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40, DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles
@compiles(BigInteger, "sqlite")
def _b(t, c, **kw): return "INTEGER"

from school_setup import give_teachers_their_subjects
from src import create_app
from src.db import db
from src.models import Admin, Teacher, Course, Subject, Section, Student, Assignment, AssignmentSubmission
import src.services.assignment_submission as submission_service

UPLOADS = os.path.join(SP, "test_uploads")
shutil.rmtree(UPLOADS, ignore_errors=True)
submission_service.UPLOAD_FOLDER = UPLOADS          # keep test files out of the repo

app = create_app()
client = app.test_client()
fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:120]}" if extra != "" else ""))
    if not cond: fails.append(name)

def make(cls, name, uname, email, pw="secret1", **kw):
    u = cls(name=name, username=uname, email=email, **kw); u.set_password(pw); return u

with app.app_context():
    db.create_all()
    admin = make(Admin, "Root", "root", "root@x.com")
    sara = make(Teacher, "Sara", "sara", "sara@x.com"); omar = make(Teacher, "Omar", "omar", "omar@x.com")
    db.session.add_all([admin, sara, omar]); db.session.commit()
    course = Course(name="CS", course_code="CS1", teacher_id=sara.id); sec = Section(name="A", teacher_id=sara.id)
    db.session.add_all([course, sec]); db.session.commit()
    maths = Subject(name="Maths", teacher_id=sara.id, course_id=course.id)
    ali = make(Student, "Ali", "ali", "ali@x.com", section_id=sec.id)
    bilal = make(Student, "Bilal", "bilal", "bilal@x.com", section_id=sec.id)
    db.session.add_all([maths, ali, bilal]); db.session.commit()
    hw = Assignment(title="HW", subject_id=maths.id, teacher_id=sara.id, due_date=(datetime.date.today() + datetime.timedelta(days=30)), description="d")
    db.session.add(hw); db.session.commit()
    give_teachers_their_subjects()
    HW = hw.id; ALI = ali.id

def login(email, pw="secret1"):
    r = client.post("/api/login", json={"email": email, "password": pw})
    return r.get_json().get("token"), r.status_code

def auth(tok): return {"Authorization": f"Bearer {tok}"}

T = {k: login(f"{k}@x.com")[0] for k in ["root", "sara", "omar", "ali", "bilal"]}

print("--- 1. Admin creation")
r = client.post("/api/add/admin", json={"name": "Hacker", "username": "hacker", "email": "h@x.com", "password": "secret1"})
check("public POST /api/add/admin no longer exists", r.status_code in (404, 405), r.status_code)

print("--- 2. Passwords")
with app.app_context():
    check("stored passwords are bcrypt hashes", Student.query.get(ALI).password.startswith("$2b$"))
r = client.put(f"/api/update/student?id={ALI}", json={"password": "newpass1"}, headers=auth(T["root"]))
check("admin updates a student's password", r.status_code == 200, r.get_json())
with app.app_context():
    stored = Student.query.get(ALI).password
check("updated password is hashed, not plain text", stored.startswith("$2b$") and stored != "newpass1", stored[:10])
tok, code = login("ali@x.com", "newpass1")
check("student logs in with the new password", code == 200 and tok, code)
T["ali"] = tok

print("--- 3. My account")
r = client.get("/api/account", headers=auth(T["ali"]))
check("GET /api/account shows own details", r.get_json()["account"]["username"] == "ali", r.get_json())
r = client.put("/api/account/username", json={"username": "bilal"}, headers=auth(T["ali"]))
check("can't take another user's username", r.status_code == 400 and r.get_json()["message"] == "Username already exists", r.get_json())
r = client.put("/api/account/username", json={"username": "root"}, headers=auth(T["ali"]))
check("can't take the admin's username either", r.status_code == 400)
r = client.put("/api/account/username", json={"username": "ali.khan"}, headers=auth(T["ali"]))
body = r.get_json()
check("username change works and returns a new token", r.status_code == 200 and body.get("token"), body.get("message"))
new_tok = body.get("token")
r = client.get("/api/account", headers=auth(new_tok))
check("new token works and shows the new username", r.get_json()["account"]["username"] == "ali.khan")
r = client.get("/api/get/student", headers=auth(T["root"]))
names = [s.get("username") for s in (r.get_json() if isinstance(r.get_json(), list) else r.get_json().get("data", r.get_json().get("students", [])))]
check("admin's student list shows the new username", "ali.khan" in names, names)

r = client.put("/api/account/password", json={"current_password": "wrong", "new_password": "another1"}, headers=auth(new_tok))
check("password change needs the right current password", r.status_code == 400, r.get_json())
r = client.put("/api/account/password", json={"current_password": "newpass1", "new_password": "newpass1"}, headers=auth(new_tok))
check("new password must differ", r.status_code == 400)
r = client.put("/api/account/password", json={"current_password": "newpass1", "new_password": "short"}, headers=auth(new_tok))
check("new password must be at least 6 characters", r.status_code == 400)
r = client.put("/api/account/password", json={"current_password": "newpass1", "new_password": "another1"}, headers=auth(new_tok))
check("password change works", r.status_code == 200, r.get_json())
check("old password no longer works", login("ali@x.com", "newpass1")[1] == 401)
tok, code = login("ali@x.com", "another1")
check("new password works", code == 200)
T["ali"] = tok
r = client.put("/api/account/password", json={"current_password": "secret1", "new_password": "teach123"}, headers=auth(T["sara"]))
check("teacher can change own password", r.status_code == 200)
T["sara"] = login("sara@x.com", "teach123")[0]
old_root_token = T["root"]
r = client.put("/api/account/username", json={"username": "admin.root"}, headers=auth(T["root"]))
check("admin can change own username", r.status_code == 200)
T["root"] = r.get_json()["token"]
r = client.get("/api/account", headers=auth(old_root_token))
check("old token is blocked after a username change", r.status_code == 401, r.status_code)

print("--- 4. Uploads")
def submit(tok, filename, content=b"hello"):
    data = {"assignment_id": str(HW), "submission_text": "my work", "submission_file": (io.BytesIO(content), filename)}
    return client.post("/api/submit/assignment", data=data, headers=auth(tok), content_type="multipart/form-data")

r = submit(T["ali"], "../../app.py")
check("path-traversal .py upload rejected", r.status_code == 400, r.get_json())
check("nothing written outside the upload folder", not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app.py.bak")))
r = submit(T["ali"], "../../../notes.pdf", b"%PDF-1 ali")
check("pdf upload accepted", r.status_code == 201, r.get_json())
saved = os.listdir(UPLOADS)
check("saved inside upload folder with random prefix and safe name", len(saved) == 1 and saved[0].endswith("_notes.pdf") and ".." not in saved[0], saved)
r = submit(T["bilal"], "notes.pdf", b"%PDF-1 bilal")
check("same filename from another student doesn't overwrite", r.status_code == 201 and len(os.listdir(UPLOADS)) == 2)
r = submit(T["ali"], "big.pdf", b"x" * (11 * 1024 * 1024))
check("files over 10 MB rejected with JSON 413", r.status_code == 413 and r.get_json()["status"] == "failed", r.status_code)
r = client.get("/static/submissions/" + saved[0])
check("files not publicly served at /static", r.status_code == 404, r.status_code)
r = client.post("/api/submit/assignment", data={"assignment_id": "9999", "submission_text": "x"}, headers=auth(T["ali"]), content_type="multipart/form-data")
check("submitting to a missing assignment gives 404, not a crash", r.status_code == 404, r.status_code)

with app.app_context():
    ali_sub = AssignmentSubmission.query.filter_by(student_id=ALI).first().id
r = client.get(f"/api/submission/file?id={ali_sub}")
check("download needs login", r.status_code == 401, r.status_code)
r = client.get(f"/api/submission/file?id={ali_sub}", headers=auth(T["ali"]))
check("student downloads own file with original name", r.status_code == 200 and r.data == b"%PDF-1 ali" and 'filename=notes.pdf' in r.headers.get("Content-Disposition", ""), r.headers.get("Content-Disposition"))
r = client.get(f"/api/submission/file?id={ali_sub}", headers=auth(T["bilal"]))
check("other student can't download it", r.status_code == 403)
r = client.get(f"/api/submission/file?id={ali_sub}", headers=auth(T["sara"]))
check("assignment's teacher can download it", r.status_code == 200)
r = client.get(f"/api/submission/file?id={ali_sub}", headers=auth(T["omar"]))
check("another teacher can't download it", r.status_code == 403)
r = client.get(f"/api/submission/file?id={ali_sub}", headers=auth(T["root"]))
check("admin can't download it (teachers check submissions)", r.status_code == 403)

print("--- 5. Submission permissions")
r = client.put(f"/api/update/submission?id={ali_sub}", json={"marks": "100", "feedback": "self-graded"}, headers=auth(T["ali"]))
check("student can't change marks", r.status_code == 403, r.get_json())
r = client.delete(f"/api/delete/submission?id={ali_sub}", headers=auth(T["ali"]))
check("student can't delete a submission", r.status_code == 403, r.get_json())
r = client.get(f"/api/get/submissions/by/assignment?id={HW}", headers=auth(T["ali"]))
check("student can't list everyone's submissions", r.status_code == 403)
r = client.put(f"/api/update/submission?id={ali_sub}", json={"marks": "50"}, headers=auth(T["omar"]))
check("other teacher can't grade it", r.status_code == 403)
r = client.put(f"/api/update/submission?id={ali_sub}", json={"marks_obtained": "88", "feedback": "Good", "submission_text": "changed!"}, headers=auth(T["sara"]))
check("assignment's teacher grades it", r.status_code == 200, r.get_json())
with app.app_context():
    s = AssignmentSubmission.query.get(ali_sub)
    check("marks and feedback saved, student's text unchanged", float(s.marks) == 88 and s.feedback == "Good" and s.submission_text == "my work", (s.marks, s.feedback, s.submission_text))
r = client.get(f"/api/get/submissions/by/assignment?id={HW}", headers=auth(T["sara"]))
check("teacher lists submissions for own assignment", r.status_code == 200)
r = client.delete(f"/api/delete/submission?id={ali_sub}", headers=auth(T["omar"]))
check("other teacher can't delete it", r.status_code == 403)
r = client.delete(f"/api/delete/submission?id={ali_sub}", headers=auth(T["root"]))
check("admin can't delete it", r.status_code == 403)
r = client.delete(f"/api/delete/submission?id={ali_sub}", headers=auth(T["sara"]))
check("assignment's teacher can delete it", r.status_code == 200)

shutil.rmtree(UPLOADS, ignore_errors=True)
print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
