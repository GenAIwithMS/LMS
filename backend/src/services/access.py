from flask import jsonify
from src.models import Student, Subject, Section, Assignment, Announcement, TeachingAssignment


# Who can reach what. Used by both the website routes and the chatbot tools,
# so both follow the same rules.
#
# The admin decides who teaches what:
# - each section (like 5-A) has a class incharge (Section.teacher_id)
# - each subject in each section has a subject teacher (TeachingAssignment)
#
# A teacher can reach:
# - the subjects they teach (in the sections where they teach them)
# - the sections they lead as class incharge, and the sections where they teach
# - the students in those sections
# - the assignments they created


def get_teacher_teaching(teacher_id):
    """The teacher's teaching assignments: which subject they teach in which section."""
    return TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()


def teacher_teaches(teacher_id, section_id, subject_id):
    """True if this teacher teaches this subject in this section."""
    teaching = TeachingAssignment.query.filter_by(teacher_id=teacher_id, section_id=section_id, subject_id=subject_id).first()
    return teaching is not None


def teacher_teaches_student_subject(teacher_id, student_id, subject_id):
    """True if this teacher teaches this subject in the student's section.

    Only that teacher may enter marks or subject attendance for the student.
    """
    student = Student.query.get(student_id)
    if not student:
        return False
    return teacher_teaches(teacher_id, student.section_id, subject_id)


def teacher_is_incharge(teacher_id, section_id):
    """True if this teacher is the class incharge of this section."""
    section = Section.query.get(section_id)
    if not section:
        return False
    return section.teacher_id == teacher_id


def incharge_clash_message(teacher_id, section_id=None):
    """A teacher can be the class incharge of only one section at a time.

    Before making teacher_id the incharge of section_id (None for a new section):
    an error message if they already lead another section, otherwise None.
    """
    if not teacher_id:
        return None
    other = Section.query.filter_by(teacher_id=teacher_id).first()
    if other and other.id != section_id:
        teacher_name = other.teacher.name
        return (f"{teacher_name} is already the class incharge of {other.full_name()}. "
                f"A teacher can lead only one section; choose another teacher or remove {teacher_name} from {other.full_name()} first.")
    return None


def user_can_view_section(role, user_id, section_id):
    """True if this user may see a section's timetable, diary and syllabus progress:
    the admin, any teacher who leads or teaches in the section, and its own students."""
    if role == "admin":
        return True
    if role == "teacher":
        return section_id in get_teacher_section_ids(user_id)
    if role == "student":
        student = Student.query.get(user_id)
        return student is not None and student.section_id == section_id
    return False


def get_teacher_subject_ids(teacher_id):
    """IDs of the subjects this teacher teaches (in any section)."""
    subject_ids = []
    for teaching in get_teacher_teaching(teacher_id):
        if teaching.subject_id not in subject_ids:
            subject_ids.append(teaching.subject_id)
    return subject_ids


def get_teacher_section_ids(teacher_id):
    """IDs of the sections this teacher leads as class incharge, or teaches a subject in."""
    section_ids = []

    sections = Section.query.filter_by(teacher_id=teacher_id).all()
    for section in sections:
        section_ids.append(section.id)

    for teaching in get_teacher_teaching(teacher_id):
        if teaching.section_id not in section_ids:
            section_ids.append(teaching.section_id)

    return section_ids


def get_teacher_student_ids(teacher_id):
    """IDs of the students in this teacher's sections."""
    student_ids = []
    for section_id in get_teacher_section_ids(teacher_id):
        students = Student.query.filter_by(section_id=section_id).all()
        for student in students:
            student_ids.append(student.id)
    return student_ids


def get_teacher_assignment_ids(teacher_id):
    """IDs of the assignments this teacher created."""
    assignment_ids = []
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    for assignment in assignments:
        assignment_ids.append(assignment.id)
    return assignment_ids


def get_student_assignment_ids(student_id):
    """IDs of the assignments a student can see and submit: ones for the student's
    section, set by the teacher who teaches that subject there."""
    assignment_ids = []
    student = Student.query.get(student_id)
    if not student:
        return assignment_ids

    assignments = Assignment.query.all()
    for assignment in assignments:
        # An assignment for another section is not for this student
        if assignment.section_id is not None and assignment.section_id != student.section_id:
            continue
        if teacher_teaches(assignment.teacher_id, student.section_id, assignment.subject_id):
            assignment_ids.append(assignment.id)

    return assignment_ids


def teacher_owns_assignment(teacher_id, assignment_id):
    """True if the teacher created this assignment."""
    return int(assignment_id) in get_teacher_assignment_ids(teacher_id)


def announcement_reaches(announcement, audience, section_ids, class_ids):
    """True if the announcement is for this audience ("teachers" or "students") and covers
    one of these sections or classes (or the whole school)."""
    if announcement.target_audience not in ["all", audience]:
        return False
    # The whole school
    if announcement.section_id is None and announcement.class_id is None:
        return True
    if announcement.section_id is not None and announcement.section_id in section_ids:
        return True
    if announcement.section_id is None and announcement.class_id in class_ids:
        return True
    return False


def get_student_announcement_ids(student_id):
    """IDs of the announcements a student can see: for everyone or for students, and for
    the whole school, the student's class, or the student's section."""
    announcement_ids = []
    student = Student.query.get(student_id)
    if not student:
        return announcement_ids

    section_ids = [student.section_id]
    class_ids = []
    if student.section and student.section.class_id:
        class_ids.append(student.section.class_id)

    for announcement in Announcement.query.all():
        if announcement_reaches(announcement, "students", section_ids, class_ids):
            announcement_ids.append(announcement.id)
    return announcement_ids


def get_teacher_announcement_ids(teacher_id):
    """IDs of the announcements a teacher can see: their own, and ones for everyone or for
    teachers, for the whole school or a class or section they lead or teach in."""
    announcement_ids = []
    section_ids = get_teacher_section_ids(teacher_id)
    class_ids = []
    for section_id in section_ids:
        section = Section.query.get(section_id)
        if section and section.class_id and section.class_id not in class_ids:
            class_ids.append(section.class_id)

    for announcement in Announcement.query.all():
        if announcement.teacher_id == teacher_id:
            announcement_ids.append(announcement.id)
        elif announcement_reaches(announcement, "teachers", section_ids, class_ids):
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


def find_teacher_student_by_id(teacher_id, student_id):
    """Find a student by ID among this teacher's students. Returns None if not found."""
    if int(student_id) not in get_teacher_student_ids(teacher_id):
        return None
    return Student.query.get(int(student_id))


def find_record(model, record_id, record_name):
    """Find a record by its ID, or by name when no ID was sent. Returns None if not found.

    Forms should send the ID: names can repeat (two teachers called "Ali"), IDs can't.
    The name is still accepted for older requests and the chatbot.
    """
    if record_id:
        return model.query.get(int(record_id))
    if record_name:
        return model.query.filter_by(name=record_name).first()
    return None


def find_teacher_subject(teacher_id, subject_name, subject_id=None):
    """Find a subject (by ID, or by name) among the subjects this teacher teaches. Returns None if not found."""
    allowed_ids = get_teacher_subject_ids(teacher_id)

    if subject_id:
        if int(subject_id) in allowed_ids:
            return Subject.query.get(int(subject_id))
        return None

    subjects = Subject.query.filter_by(name=subject_name).all()
    for subject in subjects:
        if subject.id in allowed_ids:
            return subject
    return None


def find_teacher_section(teacher_id, section_name, section_id=None):
    """Find a section (by ID, or by name) among this teacher's sections. Returns None if not found."""
    allowed_ids = get_teacher_section_ids(teacher_id)

    if section_id:
        if int(section_id) in allowed_ids:
            return Section.query.get(int(section_id))
        return None

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
