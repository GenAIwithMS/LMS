"""Scoping tests: teachers limited to their own data, duplicate names, student announcements,
and the student attendance HTTP route. No LLM calls; in-memory SQLite."""
import os, sys, datetime
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40, DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"

from src import create_app
from src.db import db
from src.models import (Teacher, Course, Subject, Section, Student, Result, Assignment,
                        AssignmentSubmission, Announcement, Attendance)
from flask_jwt_extended import create_access_token

app = create_app()
fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond:
        fails.append(name)

def user(name, uname, email, cls, **kw):
    u = cls(name=name, username=uname, email=email, **kw); u.set_password("pw"); return u

with app.app_context():
    db.create_all()
    sara = user("Sara", "sara", "sara@x", Teacher); omar = user("Omar", "omar", "omar@x", Teacher)
    db.session.add_all([sara, omar]); db.session.commit()
    cs = Course(name="CS", course_code="CS1", teacher_id=sara.id); ph = Course(name="PH", course_code="PH1", teacher_id=omar.id)
    secA = Section(name="A", teacher_id=sara.id); secB = Section(name="B", teacher_id=omar.id)
    db.session.add_all([cs, ph, secA, secB]); db.session.commit()
    maths = Subject(name="Maths", teacher_id=sara.id, course_id=cs.id)
    physics = Subject(name="Physics", teacher_id=omar.id, course_id=ph.id)
    ali1 = user("Ali", "ali.khan", "a1@x", Student, section_id=secA.id)
    ali2 = user("Ali", "ali.raza", "a2@x", Student, section_id=secA.id)
    bilal = user("Bilal", "bilal", "b@x", Student, section_id=secA.id)
    ali3 = user("Ali", "ali.shah", "a3@x", Student, section_id=secB.id)
    zara = user("Zara", "zara", "z@x", Student, section_id=secB.id)
    db.session.add_all([maths, physics, ali1, ali2, bilal, ali3, zara]); db.session.commit()
    r_maths = Result(subject_id=maths.id, student_id=bilal.id, total_marks=20, obtained_marks=15, exam_type="quiz", grade="B")
    r_phys = Result(subject_id=physics.id, student_id=zara.id, total_marks=20, obtained_marks=18, exam_type="quiz", grade="A")
    a_sara = Assignment(title="Algebra", subject_id=maths.id, teacher_id=sara.id, due_date=(datetime.date.today() + datetime.timedelta(days=30)), description="d")
    a_omar = Assignment(title="Optics", subject_id=physics.id, teacher_id=omar.id, due_date=(datetime.date.today() + datetime.timedelta(days=30)), description="d")
    db.session.add_all([r_maths, r_phys, a_sara, a_omar]); db.session.commit()
    sub_omar = AssignmentSubmission(student_id=zara.id, assignment_id=a_omar.id, submission_text="x")
    ann_b = Announcement(id=1, title="B trip", content="c", teacher_id=omar.id, section_id=secB.id)
    ann_all = Announcement(id=2, title="Holiday", content="c", teacher_id=omar.id, section_id=None)
    att_phys = Attendance(student_id=zara.id, subject_id=physics.id, status="present")
    att_ali1 = Attendance(student_id=ali1.id, subject_id=maths.id, status="present")
    db.session.add_all([sub_omar, ann_b, ann_all, att_phys, att_ali1]); db.session.commit()
    I = {k: v.id for k, v in dict(sara=sara, omar=omar, ali1=ali1, ali2=ali2, ali3=ali3, zara=zara, bilal=bilal,
                                   r_maths=r_maths, r_phys=r_phys, a_sara=a_sara, a_omar=a_omar, sub_omar=sub_omar).items()}

def token(role, uid):
    with app.app_context():
        return create_access_token(identity=str(uid), additional_claims={"role": role})

def as_user(role, uid):
    return app.test_request_context(headers={"Authorization": f"Bearer {token(role, uid)}"})

from src.agent import tools as T

with app.app_context():
    print("--- Teacher Sara: only her students and subjects")
    with as_user("teacher", I["sara"]):
        r = T.get_students.invoke({})
        names = sorted(f'{s["name"]}#{s["id"]}' for s in r["data"])
        check("get_students = section A only", {s["id"] for s in r["data"]} == {I["ali1"], I["ali2"], I["bilal"]}, names)

        r = T.mark_attendance.invoke({"status": "present", "student_name": "Ali", "subject_name": "Maths"})
        check("two Alis in her scope -> needs_clarification", r.get("status") == "needs_clarification" and len(r["candidates"]) == 2, r)
        check("candidates exclude Omar's Ali", I["ali3"] not in {c["student_id"] for c in r.get("candidates", [])}, r.get("candidates"))

        r = T.mark_attendance.invoke({"status": "present", "student_id": I["ali2"], "subject_name": "maths"})
        check("retry with student_id works (case-insensitive subject)", r.get("status") == "success", r)

        r = T.mark_attendance.invoke({"status": "present", "student_name": "Bilal", "subject_name": "Maths"})
        check("unique name works directly", r.get("status") == "success", r)

        r = T.mark_attendance.invoke({"status": "present", "student_name": "Zara", "subject_name": "Maths"})
        check("other teacher's student blocked", r.get("status") == "failed", r)

        r = T.mark_attendance.invoke({"status": "present", "student_id": I["ali3"], "subject_name": "Maths"})
        check("other teacher's student blocked by ID too", r.get("status") == "failed", r)

        r = T.mark_attendance.invoke({"status": "present", "student_name": "Bilal", "subject_name": "Physics"})
        check("subject she doesn't teach blocked", r.get("status") == "failed", r)

        r = T.get_results.invoke({})
        check("get_results = Maths only", [x["id"] for x in r["data"]] == [I["r_maths"]], r)
        check("get_result on Physics result blocked", T.get_result.invoke({"result_id": I["r_phys"]}).get("status") == "failed")
        check("update_result on Physics result blocked", T.update_result.invoke({"result_id": I["r_phys"], "obtained_marks": 0}).get("status") == "failed")
        check("remove_result on Physics result blocked", T.remove_result.invoke({"result_id": I["r_phys"]}).get("status") == "failed")

        r = T.add_result_tool.invoke({"total_marks": 20, "obtained_marks": 10, "exam_type": "quiz", "student_name": "Ali", "subject_name": "Maths"})
        check("add_result with duplicate name -> needs_clarification", r.get("status") == "needs_clarification", r)

        r = T.create_assignment.invoke({"title": "X", "description": "d", "due_date": "2026-12-05", "total_marks": 10, "subject_name": "Physics"})
        check("create_assignment in Physics blocked", r.get("status") == "failed", r)

        r = T.get_assignments.invoke({})
        check("get_assignments = her own only", [a["id"] for a in r["assignments"]] == [I["a_sara"]], r)
        check("get_assignment on Omar's blocked", T.get_assignment.invoke({"assignment_id": I["a_omar"]}).get("status") == "failed")
        check("remove_assignment on Omar's blocked", T.remove_assignment.invoke({"assignment_id": I["a_omar"]}).get("status") == "failed")
        check("submissions for Omar's assignment blocked", T.get_submissions_by_assignment_tool.invoke({"assignment_id": I["a_omar"]}).get("status") == "failed")
        check("grading a submission to Omar's assignment blocked", T.update_submission_tool.invoke({"submission_id": I["sub_omar"], "marks": 10}).get("status") == "failed")

        r = T.get_all_attendance_tool.invoke({})
        check("get_all_attendance = Maths records only", all(x["subject_name"] == "Maths" for x in r["data"]) and len(r["data"]) == 3, r)
        r = T.get_attendance_by_subject_tool.invoke({"subject_name": "Physics"})
        check("attendance for Physics blocked", r.get("status") == "failed", r)

        r = T.create_announcement.invoke({"title": "Test", "content": "c", "section_name": "A"})
        check("announcement to her section works", r.get("status") == "success", r)
        r = T.create_announcement.invoke({"title": "Nope", "content": "c", "section_name": "B"})
        check("announcement to Omar's section blocked", r.get("status") == "failed", r)
        check("editing Omar's announcement blocked", T.update_announcement.invoke({"announcement_title": "B trip", "content": "hacked"}).get("status") == "failed")
        check("deleting Omar's announcement blocked", T.remove_announcement.invoke({"announcement_title": "B trip"}).get("status") == "failed")

    print("--- Students: announcements for own section + school-wide only")
    with as_user("student", I["ali1"]):
        r = T.get_announcements.invoke({})
        titles = sorted(a["title"] for a in r["data"])
        check("section A student sees Test + Holiday, not B trip", titles == ["Holiday", "Test"], titles)
        check("get_announcement on B trip blocked", T.get_announcement.invoke({"announcement_title": "B trip"}).get("status") == "failed")
        r = T.get_my_attendance.invoke({})
        check("get_my_attendance = own records only", r.get("count") == 1, r)

    print("--- Admin: unrestricted, but duplicate names still clarified")
    with as_user("admin", 1):
        check("admin get_students sees all 5", len(T.get_students.invoke({})["data"]) == 5)
        r = T.get_enrollments_by_student_tool.invoke({"student_name": "Ali"})
        check("admin lookup of 'Ali' -> 3 candidates", r.get("status") == "needs_clarification" and len(r["candidates"]) == 3, r)
        check("admin sees all results", len(T.get_results.invoke({})["data"]) == 2)

print("--- Website route: GET /api/get/attendance")
client = app.test_client()
for who, uid, expected in [("ali1", I["ali1"], 1), ("ali2", I["ali2"], 1), ("ali3", I["ali3"], 0)]:
    resp = client.get("/api/get/attendance?student_name=Zara", headers={"Authorization": f"Bearer {token('student', uid)}"})
    body = resp.get_json()
    check(f"student {who} gets only own records (asked for Zara's)", resp.status_code == 200 and isinstance(body, list) and len(body) == expected, (resp.status_code, body))
resp = client.get("/api/get/attendance", headers={"Authorization": f"Bearer {token('teacher', I['sara'])}"})
check("teacher route now only returns her own subjects' records", resp.status_code == 200 and len(resp.get_json()) == 3, len(resp.get_json()))

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
