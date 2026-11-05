"""Fixes from the reliability test: saves that clash are retried (or answered 409, not 500),
login protection per account (kept in the database), the bell's short announcement list,
and a promoted student's earlier work staying visible. In-memory SQLite."""
import io, os, shutil, sys, tempfile
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:", LOGIN_MAX_FAILURES="3", LOGIN_LOCK_MINUTES="15")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from datetime import timedelta
from sqlalchemy.exc import OperationalError, IntegrityError
from src import create_app
from src.db import db, pakistan_time
from src.models import Admin, Teacher, Student, LoginFailure
from src.services.save_retry import save_with_retry, is_save_conflict, CONFLICT_MESSAGE
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

with app.app_context():
    db.create_all()
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id


class FakeDatabaseError(Exception):
    pass

def database_error(kind, code):
    """A SQLAlchemy error carrying a MySQL error number, like the real ones."""
    original = FakeDatabaseError(code, "test")
    return kind("UPDATE ...", {}, original)


print("--- Saving again when two saves clash")
with app.app_context(), app.test_request_context():
    tries = {"n": 0}
    def clashes_once():
        tries["n"] += 1
        if tries["n"] == 1:
            raise database_error(OperationalError, 1020)
        return "saved"
    check("a save that clashes once is tried again and works", save_with_retry(clashes_once) == "saved" and tries["n"] == 2, tries)

    def always_clashes():
        raise database_error(OperationalError, 1213)
    body, status = save_with_retry(always_clashes)
    check("a save that keeps clashing answers 409 with a clear message", status == 409 and body.get_json()["message"] == CONFLICT_MESSAGE)

    def duplicate_row():
        raise database_error(IntegrityError, 1062)
    check("two saves adding the same new row count as a clash", save_with_retry(duplicate_row, attempts=2)[1] == 409)

    def other_error():
        raise database_error(OperationalError, 2006)
    try:
        save_with_retry(other_error)
        check("other database errors are not hidden", False)
    except OperationalError:
        check("other database errors are not hidden", True)
    check("a clash is recognised; a lost connection is not",
          is_save_conflict(database_error(OperationalError, 1020)) and not is_save_conflict(database_error(OperationalError, 2006)))


print("--- Login protection per account (in the database)")
def login(email, password):
    return client.post("/api/login", json={"email": email, "password": password})
for i in range(3):
    login("sara@x.com", "wrongpass")
r = login("sara@x.com", "secret1")
check("after 3 wrong passwords, even the right one is paused", r.status_code == 429 and "wrong passwords" in r.get_json()["message"], r.get_json())
r = login("SARA@x.com", "secret1")
check("typing the email in capitals doesn't get around it", r.status_code == 429, r.get_json())
r = login("root@x.com", "secret1")
check("other accounts are not affected", r.status_code == 200)
with app.app_context():
    LoginFailure.query.update({"failed_at": pakistan_time().replace(tzinfo=None) - timedelta(minutes=20)})
    db.session.commit()
r = login("sara@x.com", "secret1")
check("after the lock time the right password works", r.status_code == 200, r.get_json())
with app.app_context():
    check("a good login clears the account's count", LoginFailure.query.filter_by(email="sara@x.com").count() == 0)
login("sara@x.com", "wrongpass")
r = login("sara@x.com", "secret1")
check("one wrong password doesn't pause the account", r.status_code == 200)

H = {"root": {"Authorization": "Bearer " + login("root@x.com", "secret1").get_json()["token"]},
     "sara": {"Authorization": "Bearer " + login("sara@x.com", "secret1").get_json()["token"]}}


print("--- The bell's short announcement list")
for i in range(6):
    client.post("/api/admin/announcements", json={"title": f"Notice {i}", "content": "x", "target_audience": "all"}, headers=H["root"])
everything = client.get("/api/get/announcements", headers=H["sara"]).get_json()
newest = client.get("/api/get/announcements?limit=2", headers=H["sara"]).get_json()
check("the full list has all 6", len(everything) == 6, len(everything))
check("?limit=2 gives the newest 2", [a["title"] for a in newest] == ["Notice 5", "Notice 4"], [a["title"] for a in newest])


print("--- A promoted student's earlier work stays visible")
classes = client.get("/api/school/classes", headers=H["root"]).get_json()
CLASS_5, CLASS_6 = classes[4]["id"], classes[5]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
SIX_A = client.post(f"/api/school/classes/{CLASS_6}/sections", json={"name": "A"}, headers=H["root"]).get_json()["section_id"]
MATHS = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"]).get_json()["subject_id"]
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
client.post("/api/add/student", json={"name": "Ali", "username": "ali", "email": "ali@x.com", "password": "secret1", "section_id": A, "roll_number": "1"}, headers=H["root"])
with app.app_context():
    ALI = Student.query.filter_by(username="ali").first().id
H["ali"] = {"Authorization": "Bearer " + login("ali@x.com", "secret1").get_json()["token"]}

due = (pakistan_time().date() + timedelta(days=7)).isoformat()
client.post("/api/create/assignments", json={"title": "Handed in", "description": "x", "subject_id": MATHS, "section_id": A, "due_date": due, "total_marks": 10}, headers=H["sara"])
client.post("/api/create/assignments", json={"title": "Not handed in", "description": "x", "subject_id": MATHS, "section_id": A, "due_date": due, "total_marks": 10}, headers=H["sara"])
listed = client.get("/api/get/assignments", headers=H["ali"]).get_json()["assignments"]
HANDED = [a["id"] for a in listed if a["title"] == "Handed in"][0]
client.post("/api/submit/assignment", data={"assignment_id": str(HANDED), "submission_text": "done"}, headers=H["ali"], content_type="multipart/form-data")
test = client.post("/api/school/class-tests", json={"section_id": A, "subject_id": MATHS, "title": "Quiz", "date": pakistan_time().date().isoformat(), "total_marks": 10}, headers=H["sara"]).get_json()["test"]["id"]
client.put(f"/api/school/class-tests/{test}/marks", json={"marks": [{"student_id": ALI, "obtained_marks": 8}]}, headers=H["sara"])

r = client.post(f"/api/exams/promotion/sections/{A}", json={"target_section_id": SIX_A, "student_ids": [ALI]}, headers=H["root"])
check("Ali is promoted to 6-A", r.status_code == 200, r.get_json())
titles = [a["title"] for a in client.get("/api/get/assignments", headers=H["ali"]).get_json()["assignments"]]
check("his handed-in Class 5 assignment is still listed", "Handed in" in titles, titles)
check("but not Class 5 work he never handed in", "Not handed in" not in titles, titles)
tests = client.get("/api/school/class-tests", headers=H["ali"]).get_json()
check("his Class 5 quiz mark is still listed", [(t["title"], t["my_marks"]) for t in tests] == [("Quiz", "8")], tests)
r = client.post("/api/submit/assignment", data={"assignment_id": str(HANDED), "submission_text": "again"}, headers=H["ali"], content_type="multipart/form-data")
check("an old class's assignment can't be submitted again", r.status_code in (403, 404), r.get_json())


print("--- Students only get report cards for terms that are theirs")
CLASS_7 = classes[6]["id"]
client.post(f"/api/school/classes/{CLASS_7}/subjects", json={"name": "Maths"}, headers=H["root"])
today = pakistan_time().date()
SESSION = client.post("/api/school/sessions", json={"name": "2026-27", "start_date": (today - timedelta(days=100)).isoformat(),
                                                    "end_date": (today + timedelta(days=200)).isoformat(), "is_current": True}, headers=H["root"]).get_json()["session_id"]
term = {"session_id": SESSION, "start_date": (today - timedelta(days=10)).isoformat(), "end_date": (today - timedelta(days=1)).isoformat()}
SEVEN_ONLY = client.post("/api/exams/terms", json=dict(term, name="Class 7 Test"), headers=H["root"]).get_json()["term"]["id"]
client.post(f"/api/exams/terms/{SEVEN_ONLY}/papers", json={"class_id": CLASS_7}, headers=H["root"])
client.put(f"/api/exams/terms/{SEVEN_ONLY}", json={"is_published": True}, headers=H["root"])
names = [t["name"] for t in client.get("/api/exams/terms", headers=H["ali"]).get_json()]
check("Ali (Class 6) doesn't get a term only Class 7 sat", "Class 7 Test" not in names, names)

shutil.rmtree(UPLOADS, ignore_errors=True)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
