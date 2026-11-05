"""Fixes from the student panel test report: updating a submission keeps the earlier file
unless a new one is sent, graded work can't be replaced, and the assistant's "not set up"
message is plain for students. In-memory SQLite."""
import io, os, shutil, sys, tempfile
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from datetime import timedelta
from src import create_app
from src.db import db, pakistan_time
from src.models import Admin, Teacher, AssignmentSubmission
import src.services.assignment_submission as submission_service

# Uploaded test files go to a throwaway folder, not the real uploads folder
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

with app.app_context():
    db.create_all()
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara")}

CLASS_5 = client.get("/api/school/classes", headers=H["root"]).get_json()[4]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
MATHS = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"]).get_json()["subject_id"]
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
client.post("/api/add/student", json={"name": "Ali", "username": "ali", "email": "ali@x.com", "password": "secret1",
                                      "section_id": A, "roll_number": "1"}, headers=H["root"])
H["ali"] = login("ali")

due = (pakistan_time().date() + timedelta(days=7)).isoformat()
client.post("/api/create/assignments", json={"title": "Fractions", "description": "Ex 2.1", "subject_id": MATHS, "section_id": A, "due_date": due, "total_marks": 10}, headers=H["sara"])
listed = client.get("/api/get/assignments", headers=H["ali"]).get_json()
if isinstance(listed, dict):
    listed = listed.get("data") or listed.get("assignments") or []
HW = listed[0]["id"]

def submit(text=None, file_name=None):
    data = {"assignment_id": str(HW)}
    if text is not None:
        data["submission_text"] = text
    if file_name:
        data["submission_file"] = (io.BytesIO(b"%PDF answers"), file_name)
    return client.post("/api/submit/assignment", data=data, headers=H["ali"], content_type="multipart/form-data")

def saved():
    with app.app_context():
        sub = AssignmentSubmission.query.first()
        return sub.id, sub.submission_text, sub.submission_file


print("--- Updating a submission")
r = submit("First answers", "answers.pdf")
check("Ali submits text and a PDF", r.status_code == 201, r.get_json())
SUB, text, first_file = saved()
check("the file is saved", first_file and os.path.exists(os.path.join(UPLOADS, first_file)), first_file)

r = submit("Better answers")
check("sending only new text updates it", r.status_code == 200 and r.get_json()["message"] == "Your submission was updated", r.get_json())
SUB, text, file_now = saved()
check("the text is replaced", text == "Better answers", text)
check("the earlier file stays (not deleted)", file_now == first_file and os.path.exists(os.path.join(UPLOADS, first_file)), file_now)

r = submit(None, "new.pdf")
SUB, text, file_now = saved()
check("sending only a new file keeps the text", r.status_code == 200 and text == "Better answers", (r.get_json(), text))
check("the new file replaces the old one, which is removed", file_now != first_file and not os.path.exists(os.path.join(UPLOADS, first_file)), file_now)

client.put(f"/api/update/submission?id={SUB}", json={"marks_obtained": "8", "feedback": "Good"}, headers=H["sara"])
r = submit("Changing after grading")
check("graded work can't be replaced", r.status_code == 409, r.get_json())
mine = client.get("/api/get/submissions/by/student", headers=H["ali"]).get_json()
row = mine["data"][0]
check("Ali's list has his marks and feedback", float(row["marks"]) == 8 and row["feedback"] == "Good", row)


print("--- The assistant when it isn't set up")
r = client.post("/api/chat", json={"message": "hello"}, headers=H["ali"])
check("a student gets a plain message", r.status_code == 503 and "GROQ" not in r.get_json()["message"] and "admin" in r.get_json()["message"], r.get_json())
r = client.post("/api/chat", json={"message": "hello"}, headers=H["root"])
check("the admin gets the technical reason", r.status_code == 503 and "GROQ_API_KEY" in r.get_json()["message"], r.get_json())

shutil.rmtree(UPLOADS, ignore_errors=True)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
