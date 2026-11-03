from flask import jsonify
from src.models import Student, Subject, Section, Course, Enrollment, Assignment, Announcement


# Who can reach what. Used by both the website routes and the chatbot tools,
# so both follow the same rules.
#
# A teacher can reach:
# - subjects they teach
# - students in sections they lead, or enrolled in their courses
# - sections they lead, or sections of their students
# - assignments they created, or assignments in their subjects


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


def teacher_owns_assignment(teacher_id, assignment_id):
    """True if the teacher created this assignment or teaches its subject."""
    return int(assignment_id) in get_teacher_assignment_ids(teacher_id)


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


def find_teacher_student(teacher_id, student_name):
    """Find a student by name among this teacher's students. Returns None if not found."""
    allowed_ids = get_teacher_student_ids(teacher_id)
    students = Student.query.filter_by(name=student_name).all()
    for student in students:
        if student.id in allowed_ids:
            return student
    return None


def find_teacher_subject(teacher_id, subject_name):
    """Find a subject by name among the subjects this teacher teaches. Returns None if not found."""
    subjects = Subject.query.filter_by(name=subject_name, teacher_id=teacher_id).all()
    if subjects:
        return subjects[0]
    return None


def find_teacher_section(teacher_id, section_name):
    """Find a section by name among this teacher's sections. Returns None if not found."""
    allowed_ids = get_teacher_section_ids(teacher_id)
    sections = Section.query.filter_by(name=section_name).all()
    for section in sections:
        if section.id in allowed_ids:
            return section
    return None


def filter_response_by_ids(response, allowed_ids):
    """Take a service response (a jsonify list, or a dict holding a list) and keep
    only the rows whose "id" is in allowed_ids. Returns a new jsonify response.
    """
    status_code = 200
    if isinstance(response, tuple):
        status_code = response[1]
        response = response[0]

    data = response.get_json(silent=True)

    # Services answer "not found" (404) when a list is empty. An empty list is fine.
    if status_code == 404:
        return jsonify([]), 200

    if isinstance(data, list):
        kept_rows = []
        for row in data:
            if row.get("id") in allowed_ids:
                kept_rows.append(row)
        return jsonify(kept_rows), status_code

    if isinstance(data, dict):
        for key in ["data", "assignments"]:
            if key in data and isinstance(data[key], list):
                kept_rows = []
                for row in data[key]:
                    if row.get("id") in allowed_ids:
                        kept_rows.append(row)
                data[key] = kept_rows
        return jsonify(data), status_code

    return response, status_code
