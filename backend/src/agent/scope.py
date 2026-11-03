"""Data scoping for agent tools.

The logged-in user is identified from their JWT, never by the model. These
helpers work out which records that user may see or change, and resolve the
names the model passes in, but only within that scope.

Teacher scope:
- Subjects: subjects where Subject.teacher_id is the teacher.
- Students: students in sections the teacher leads, plus students enrolled in
  courses the teacher runs or teaches a subject in.
- Sections: sections the teacher leads, plus sections of their students.
Admins are unrestricted (None means "no limit").
"""
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import func, or_

from src.models import Student, Subject, Section, Course, Enrollment, Assignment, Announcement


def current_user():
    """Return (role, user_id) from the verified JWT."""
    return get_jwt().get("role"), int(get_jwt_identity())


def failed(message, **extra):
    return {"status": "failed", "message": message, **extra}


# --- What a teacher can reach -------------------------------------------------

def teacher_subject_ids(teacher_id):
    return {s.id for s in Subject.query.filter_by(teacher_id=teacher_id).all()}


def teacher_course_ids(teacher_id):
    led = {c.id for c in Course.query.filter_by(teacher_id=teacher_id).all()}
    via_subjects = {s.course_id for s in Subject.query.filter_by(teacher_id=teacher_id).all()}
    return led | via_subjects


def teacher_student_ids(teacher_id):
    section_ids = {s.id for s in Section.query.filter_by(teacher_id=teacher_id).all()}
    in_sections = {s.id for s in Student.query.filter(Student.section_id.in_(section_ids)).all()} if section_ids else set()
    course_ids = teacher_course_ids(teacher_id)
    enrolled = {e.student_id for e in Enrollment.query.filter(Enrollment.course_id.in_(course_ids)).all()} if course_ids else set()
    return in_sections | enrolled


def teacher_section_ids(teacher_id):
    led = {s.id for s in Section.query.filter_by(teacher_id=teacher_id).all()}
    student_ids = teacher_student_ids(teacher_id)
    of_students = {s.section_id for s in Student.query.filter(Student.id.in_(student_ids)).all()} if student_ids else set()
    return led | of_students


def allowed_student_ids():
    """Student IDs the current user may access, or None for no limit (admin)."""
    role, user_id = current_user()
    if role == "admin":
        return None
    if role == "teacher":
        return teacher_student_ids(user_id)
    if role == "student":
        return {user_id}
    return set()


def allowed_subject_ids():
    """Subject IDs the current user may access, or None for no limit (admin)."""
    role, user_id = current_user()
    if role == "admin":
        return None
    if role == "teacher":
        return teacher_subject_ids(user_id)
    return set()


def allowed_section_ids():
    role, user_id = current_user()
    if role == "admin":
        return None
    if role == "teacher":
        return teacher_section_ids(user_id)
    if role == "student":
        student = Student.query.get(user_id)
        return {student.section_id} if student else set()
    return set()


def allowed_assignment_ids():
    """Assignments the current user may access: a teacher's own, or in their subjects."""
    role, user_id = current_user()
    if role == "admin":
        return None
    if role == "teacher":
        subject_ids = teacher_subject_ids(user_id)
        query = Assignment.query.filter(or_(Assignment.teacher_id == user_id,
                                            Assignment.subject_id.in_(subject_ids)))
        return {a.id for a in query.all()}
    return set()


def student_announcement_ids(student_id):
    """Announcements for the student's own section, plus ones with no section (school-wide)."""
    student = Student.query.get(student_id)
    section_id = student.section_id if student else None
    query = Announcement.query.filter(or_(Announcement.section_id == section_id,
                                          Announcement.section_id.is_(None)))
    return {a.id for a in query.all()}


def in_scope(record_id, allowed):
    return allowed is None or record_id in allowed


# --- Resolving names inside the user's scope ----------------------------------

def _limit(query, column, allowed):
    if allowed is None:
        return query
    if not allowed:
        return None
    return query.filter(column.in_(allowed))


def resolve_student(student_name=None, student_id=None):
    """Find one student the current user may access.

    Returns (student, None) on success, or (None, error_dict). When several
    students share the name, the error lists them so the model can ask the
    user which one and call again with student_id.
    """
    allowed = allowed_student_ids()

    if student_id is not None:
        student = Student.query.get(int(student_id))
        if not student or not in_scope(student.id, allowed):
            return None, failed(f"No student with ID {student_id} among the students you can access.")
        return student, None

    if not student_name:
        return None, failed("Give a student name or student_id.")

    query = _limit(Student.query.filter(func.lower(Student.name) == student_name.strip().lower()), Student.id, allowed)
    matches = query.all() if query is not None else []
    if not matches:
        return None, failed(f"No student named '{student_name}' among the students you can access.")
    if len(matches) > 1:
        return None, {
            "status": "needs_clarification",
            "message": f"{len(matches)} students are named '{student_name}'. Ask the user which one, then call this tool again with student_id.",
            "candidates": [
                {"student_id": s.id, "name": s.name, "username": s.username,
                 "section": s.section.name if s.section else None}
                for s in matches
            ],
        }
    return matches[0], None


def resolve_subject(subject_name=None, subject_id=None):
    """Find one subject the current user may access. Same contract as resolve_student."""
    allowed = allowed_subject_ids()

    if subject_id is not None:
        subject = Subject.query.get(int(subject_id))
        if not subject or not in_scope(subject.id, allowed):
            return None, failed(f"No subject with ID {subject_id} among the subjects you teach.")
        return subject, None

    if not subject_name:
        return None, failed("Give a subject name or subject_id.")

    query = _limit(Subject.query.filter(func.lower(Subject.name) == subject_name.strip().lower()), Subject.id, allowed)
    matches = query.all() if query is not None else []
    if not matches:
        return None, failed(f"No subject named '{subject_name}' among the subjects you teach.")
    if len(matches) > 1:
        return None, {
            "status": "needs_clarification",
            "message": f"{len(matches)} subjects are named '{subject_name}'. Ask the user which one, then call this tool again with subject_id.",
            "candidates": [
                {"subject_id": s.id, "name": s.name, "course": s.course.name if s.course else None}
                for s in matches
            ],
        }
    return matches[0], None


def resolve_section(section_name):
    """Find one section the current user may access by name."""
    allowed = allowed_section_ids()
    query = _limit(Section.query.filter(func.lower(Section.name) == section_name.strip().lower()), Section.id, allowed)
    matches = query.all() if query is not None else []
    if not matches:
        return None, failed(f"No section named '{section_name}' among the sections you can access.")
    if len(matches) > 1:
        return None, failed(f"Several sections are named '{section_name}'. Ask an admin to rename one.")
    return matches[0], None


# --- Filtering list results ---------------------------------------------------

def keep_ids(result, allowed_ids):
    """Filter a tool result's list (under "data" or "assignments") to allowed record IDs."""
    if allowed_ids is None or not isinstance(result, dict):
        return result
    for key in ("data", "assignments"):
        if isinstance(result.get(key), list):
            result[key] = [row for row in result[key] if row.get("id") in allowed_ids]
            if "count" in result:
                result["count"] = len(result[key])
    return result
