import os, sys
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40, DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder
from sqlalchemy import BigInteger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.compiler import compiles
@compiles(BigInteger, "sqlite")
def _b(t, c, **kw): return "INTEGER"
from src import create_app
from src.db import db
from src.models import Teacher, Section, Student, Admin
from src.services import add_students, add_teacher, add_admin, update_student, update_teacher

app = create_app(); fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {extra}" if extra != "" else ""))
    if not cond: fails.append(name)
def out(r):
    if isinstance(r, tuple): return r[1], r[0].get_json()
    return r.status_code, r.get_json()

with app.app_context():
    db.create_all()
    check("teacher created", out(add_teacher("Sara", "sara", "sara@x.com", "pw"))[0] == 201)
    sec = Section(name="A", teacher_id=1); db.session.add(sec); db.session.commit()
    check("student created", out(add_students("Ali", "ali", sec.id, "pw", "ali@x.com"))[0] == 201)
    check("admin created", out(add_admin("Root", "root@x.com", "root", "pw"))[0] == 201)

    code, body = out(add_students("Ali2", "ali2", sec.id, "pw", "sara@x.com"))
    check("student can't reuse a teacher's email", code == 400 and body["message"] == "Email already exists", body)
    code, body = out(add_teacher("T2", "ali", "t2@x.com", "pw"))
    check("teacher can't reuse a student's username", code == 400 and body["message"] == "Username already exists", body)
    code, body = out(add_admin("A2", "ali@x.com", "a2", "pw"))
    check("admin can't reuse a student's email", code == 400, body)
    check("same-name student with new username/email is fine", out(add_students("Ali", "ali.raza", sec.id, "pw", "raza@x.com"))[0] == 201)

    ali = Student.query.filter_by(username="ali").first()
    code, body = out(update_student(ali.id, email="root@x.com"))
    check("update_student blocks an email in use", code == 400, body)
    code, body = out(update_student(ali.id, email="ali@x.com", name="Ali Khan"))
    check("update_student keeping own email works", code == 200, body)
    sara = Teacher.query.filter_by(username="sara").first()
    code, body = out(update_teacher(sara.id, username="root"))
    check("update_teacher blocks a username in use", code == 400, body)
    code, body = out(update_teacher(sara.id, username="sara.t"))
    check("update_teacher with a free username works", code == 200, body)

    db.session.add(Student(name="X", username="ali.raza", email="new@x.com", password="h", section_id=sec.id))
    try:
        db.session.commit(); ok = False
    except IntegrityError:
        db.session.rollback(); ok = True
    check("database itself rejects a duplicate username", ok)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
