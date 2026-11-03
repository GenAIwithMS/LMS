from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import func
from src.models import Student, Subject, Section, Course, Enrollment, Assignment, Announcement


# These helpers decide which records the logged-in user can reach.
# The user comes from their JWT, never from the model.
#
# A teacher can reach:
# - subjects they teach
# - students in sections they lead, or enrolled in their courses
# - sections they lead, or sections of their students
# An admin can reach everything.


def get_teacher_subject_ids(teacher_id):
    """IDs of the subjects this teacher teaches."""
    subject_ids = []
    subjects = Subject.query.filter_by(teacher_id=teacher_id).all()
    for subject in subjects:
        subject_ids.append(subject.id)
    return subject_ids


def get_teacher_course_ids(teacher_id):
    """IDs of the courses this teacher runs, or teaches a subject in."""
    course_ids = []

    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    for course in courses:
        course_ids.append(course.id)

    subjects = Subject.query.filter_by(teacher_id=teacher_id).all()
    for subject in subjects:
        if subject.course_id not in course_ids:
            course_ids.append(subject.course_id)

    return course_ids


def get_teacher_student_ids(teacher_id):
    """IDs of the students in this teacher's sections or courses."""
    student_ids = []

    sections = Section.query.filter_by(teacher_id=teacher_id).all()
    for section in sections:
        students = Student.query.filter_by(section_id=section.id).all()
        for student in students:
            if student.id not in student_ids:
                student_ids.append(student.id)

    course_ids = get_teacher_course_ids(teacher_id)
    for course_id in course_ids:
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        for enrollment in enrollments:
            if enrollment.student_id not in student_ids:
                student_ids.append(enrollment.student_id)

    return student_ids


def get_teacher_section_ids(teacher_id):
    """IDs of the sections this teacher leads, plus the sections of their students."""
    section_ids = []

    sections = Section.query.filter_by(teacher_id=teacher_id).all()
    for section in sections:
        section_ids.append(section.id)

    student_ids = get_teacher_student_ids(teacher_id)
    for student_id in student_ids:
        student = Student.query.get(student_id)
        if student and student.section_id not in section_ids:
            section_ids.append(student.section_id)

    return section_ids


def get_teacher_assignment_ids(teacher_id):
    """IDs of the teacher's own assignments, and assignments in their subjects."""
    assignment_ids = []

    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    for assignment in assignments:
        assignment_ids.append(assignment.id)

    subject_ids = get_teacher_subject_ids(teacher_id)
    for subject_id in subject_ids:
        assignments = Assignment.query.filter_by(subject_id=subject_id).all()
        for assignment in assignments:
            if assignment.id not in assignment_ids:
                assignment_ids.append(assignment.id)

    return assignment_ids


def get_student_announcement_ids(student_id):
    """IDs of announcements for the student's section, plus ones with no section (school-wide)."""
    announcement_ids = []
    student = Student.query.get(student_id)

    announcements = Announcement.query.all()
    for announcement in announcements:
        if announcement.section_id is None:
            announcement_ids.append(announcement.id)
        elif student and announcement.section_id == student.section_id:
            announcement_ids.append(announcement.id)

    return announcement_ids


def filter_by_ids(result, allowed_ids):
    """Keep only the rows whose "id" is in allowed_ids.

    Works on tool results that hold their rows under "data" or "assignments".
    """
    if not isinstance(result, dict):
        return result

    for key in ["data", "assignments"]:
        if key in result and isinstance(result[key], list):
            kept_rows = []
            for row in result[key]:
                if row.get("id") in allowed_ids:
                    kept_rows.append(row)
            result[key] = kept_rows

            if "count" in result:
                result["count"] = len(kept_rows)

    return result


def find_student(student_name=None, student_id=None):
    """Find one student the logged-in user can reach.

    Returns (student, None) when found, or (None, error) when not.
    When several students share the name, error has status "needs_clarification"
    and lists them, so the model can ask the user and call again with student_id.
    """
    token = get_jwt()
    role = token.get("role")
    user_id = int(get_jwt_identity())

    allowed_ids = None
    if role == "teacher":
        allowed_ids = get_teacher_student_ids(user_id)

    if student_id is not None:
        student = Student.query.get(int(student_id))
        if not student:
            return None, {"message": f"No student with ID {student_id}", "status": "failed"}
        if allowed_ids is not None and student.id not in allowed_ids:
            return None, {"message": f"No student with ID {student_id} among the students you can access", "status": "failed"}
        return student, None

    if not student_name:
        return None, {"message": "Give a student name or student_id", "status": "failed"}

    # Match the name without caring about capital letters
    students = Student.query.filter(func.lower(Student.name) == student_name.strip().lower()).all()

    matches = []
    for student in students:
        if allowed_ids is None or student.id in allowed_ids:
            matches.append(student)

    if len(matches) == 0:
        return None, {"message": f"No student named '{student_name}' among the students you can access", "status": "failed"}

    if len(matches) > 1:
        candidates = []
        for student in matches:
            candidates.append({
                "student_id": student.id,
                "name": student.name,
                "username": student.username,
                "section": student.section.name if student.section else None
            })
        return None, {
            "message": f"{len(matches)} students are named '{student_name}'. Ask the user which one, then call this tool again with student_id.",
            "status": "needs_clarification",
            "candidates": candidates
        }

    return matches[0], None


def find_subject(subject_name=None, subject_id=None):
    """Find one subject the logged-in user can reach.

    Same return values as find_student. Teachers can only reach subjects they teach.
    """
    token = get_jwt()
    role = token.get("role")
    user_id = int(get_jwt_identity())

    allowed_ids = None
    if role == "teacher":
        allowed_ids = get_teacher_subject_ids(user_id)

    if subject_id is not None:
        subject = Subject.query.get(int(subject_id))
        if not subject:
            return None, {"message": f"No subject with ID {subject_id}", "status": "failed"}
        if allowed_ids is not None and subject.id not in allowed_ids:
            return None, {"message": f"No subject with ID {subject_id} among the subjects you teach", "status": "failed"}
        return subject, None

    if not subject_name:
        return None, {"message": "Give a subject name or subject_id", "status": "failed"}

    subjects = Subject.query.filter(func.lower(Subject.name) == subject_name.strip().lower()).all()

    matches = []
    for subject in subjects:
        if allowed_ids is None or subject.id in allowed_ids:
            matches.append(subject)

    if len(matches) == 0:
        return None, {"message": f"No subject named '{subject_name}' among the subjects you teach", "status": "failed"}

    if len(matches) > 1:
        candidates = []
        for subject in matches:
            candidates.append({
                "subject_id": subject.id,
                "name": subject.name,
                "course": subject.course.name if subject.course else None
            })
        return None, {
            "message": f"{len(matches)} subjects are named '{subject_name}'. Ask the user which one, then call this tool again with subject_id.",
            "status": "needs_clarification",
            "candidates": candidates
        }

    return matches[0], None


def find_section(section_name):
    """Find one section the logged-in user can reach. Returns (section, None) or (None, error)."""
    token = get_jwt()
    role = token.get("role")
    user_id = int(get_jwt_identity())

    allowed_ids = None
    if role == "teacher":
        allowed_ids = get_teacher_section_ids(user_id)

    sections = Section.query.filter(func.lower(Section.name) == section_name.strip().lower()).all()

    matches = []
    for section in sections:
        if allowed_ids is None or section.id in allowed_ids:
            matches.append(section)

    if len(matches) == 0:
        return None, {"message": f"No section named '{section_name}' among the sections you can access", "status": "failed"}

    if len(matches) > 1:
        return None, {"message": f"Several sections are named '{section_name}'. Ask an admin to rename one.", "status": "failed"}

    return matches[0], None
