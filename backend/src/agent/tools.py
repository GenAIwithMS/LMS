import functools
from flask import Response
from langchain.tools import tool
from src.models import Subject,Student,Teacher,Course,Section,Attendance,Announcement,Result,AssignmentSubmission
from src.agent.scope import (
    current_user, failed, in_scope, keep_ids,
    allowed_student_ids, allowed_subject_ids, allowed_assignment_ids, student_announcement_ids,
    resolve_student, resolve_subject, resolve_section,
)
from flask_jwt_extended import get_jwt_identity, get_jwt,jwt_required

from src.services import add_announcement,get_all_announcements,get_announcement_by_title,edit_announcement,delete_announcement,add_event,get_event_by_id,get_all_events,update_event,delete_event,add_section,get_section_by_id,get_all_sections,edit_section,delete_section,add_students,get_all_students,get_student_by_id,update_student,delete_student,add_course,get_all_courses,get_course_by_id,update_course,delete_course,enroll_student,get_enrollments_by_course,get_enrollments_by_student,update_enrollment,delete_enrollment,get_all_enrollments,add_result, get_result_by_id, get_all_results, get_results_by_student, edit_result, delete_result,add_subject, get_all_subjects, get_subject_by_id, delete_subject,update_subject,add_teacher, get_teacher_by_id, update_teacher, delete_teacher, get_all_teachers,mark_attend, get_attendance_by_student,get_attendance_by_subject,get_all_attendance,update_attendance,delete_attendance,add_assignment, get_assignment_by_id,get_all_assignments,edit_assignment,delete_assignment,get_submissions_by_student, get_submissions_by_assignment, update_submission


def to_tool_result(result):
    """Turn a service result into plain data the model can read.

    Services return Flask responses (jsonify) or (response, status_code) tuples.
    Passed to the model as-is, they show up as "<Response 201 CREATED>" and the
    model can't tell whether the call worked.
    """
    status_code = None
    if isinstance(result, tuple):
        result, status_code = result[0], (result[1] if len(result) > 1 else None)

    if isinstance(result, Response):
        status_code = status_code or result.status_code
        result = result.get_json(silent=True)

    if isinstance(result, list):
        return {"status": "success", "count": len(result), "data": result}

    if isinstance(result, dict) and status_code and status_code >= 400:
        result.setdefault("status", "failed")

    return result


def readable_result(func):
    """Decorator: run the tool, then convert its result with to_tool_result."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return to_tool_result(func(*args, **kwargs))
    return wrapper


@tool
@readable_result
@jwt_required()
def create_announcement(title, content, section_name, target_audience = 'all', created_at = None):
    """Create a new announcement for one of your sections.

    Args:
        title: The title of the announcement
        content: The content of the announcement
        section_name: Name of the section for the announcement
        target_audience: Target audience, defaults to 'all'
        created_at: Creation timestamp, optional
    """
    role, teacher_id = current_user()
    if role != "teacher":
        return failed("Only teachers can create announcements")

    section, error = resolve_section(section_name)
    if error:
        return error
    return add_announcement(title, content, teacher_id, section.id, target_audience, created_at)

@tool
@readable_result
@jwt_required()
def get_announcements():
    """Retrieve announcements. Students only see announcements for their own section and school-wide ones. Use this tool whenever users ask about announcements."""
    role, user_id = current_user()
    if role not in ["admin", "teacher", "student"]:
        return failed("Unauthorized access")

    result = to_tool_result(get_all_announcements())
    if role == "student":
        result = keep_ids(result, student_announcement_ids(user_id))
    return result


@tool
@readable_result
@jwt_required()
def get_announcement(announcement_title):
    """Retrieve a specific announcement by its title.

    Args:
        announcement_title: The title of the announcement to retrieve
    """
    role, user_id = current_user()
    if role not in ["admin", "teacher", "student"]:
        return failed("Unauthorized access")

    if role == "student":
        announcement = Announcement.query.filter_by(title=announcement_title).first()
        if not announcement or announcement.id not in student_announcement_ids(user_id):
            return failed("Announcement not found")
    return get_announcement_by_title(announcement_title)


@tool
@readable_result
@jwt_required()
def update_announcement(announcement_title, title=None, content=None, target_audience=None, section_name=None):
    """Update one of your own announcements.

    Args:
        announcement_title: The title of the announcement to update
        title: New title (optional)
        content: New content (optional)
        target_audience: New target audience (optional)
        section_name: New section name (optional)
    """
    role, teacher_id = current_user()
    if role != "teacher":
        return failed("Only teachers can update announcements")

    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement or announcement.teacher_id != teacher_id:
        return failed("You have no announcement with that title")

    kwargs = {}
    if title is not None:
        kwargs['title'] = title
    if content is not None:
        kwargs['content'] = content
    if target_audience is not None:
        kwargs['target_audience'] = target_audience
    if section_name is not None:
        section, error = resolve_section(section_name)
        if error:
            return error
        kwargs['section_id'] = section.id
    return edit_announcement(announcement_title, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_announcement(announcement_title):
    """Delete one of your own announcements.

    Args:
        announcement_title: The title of the announcement to delete
    """
    role, teacher_id = current_user()
    if role != "teacher":
        return failed("Only teachers can delete announcements")

    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement or announcement.teacher_id != teacher_id:
        return failed("You have no announcement with that title")
    return delete_announcement(announcement_title)
@tool
@readable_result
@jwt_required()
def create_event(title, description, event_date, event_time):
    """Create a new event in the LMS system.
    
    Args:
        title: The title of the event
        description: Description of the event
        event_date: Date of the event
        event_time: Time of the event
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create events", "status": "failed"}
    admin_id = int(get_jwt_identity())

    return add_event(title, description, event_date, event_time, admin_id)


@tool
@readable_result
@jwt_required()
def get_event(event_id):
    """Retrieve a specific event by its ID. Use this tool when users ask about a specific event.
    
    Args:
        event_id: The ID of the event to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_event_by_id(event_id)


@tool
@readable_result
@jwt_required()
def get_events():
    """Retrieve all events from the LMS system. Use this tool when users ask about events."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_events()


@tool
@readable_result
@jwt_required()
def update_event_tool(event_id, title=None, description=None, event_date=None, event_time=None):
    """Update an existing event.
    
    Args:
        event_id: The ID of the event to update
        title: New title (optional)
        description: New description (optional)
        event_date: New event date (optional)
        event_time: New event time (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update events", "status": "failed"}
    kwargs = {}
    if title is not None:
        kwargs['title'] = title
    if description is not None:
        kwargs['description'] = description
    if event_date is not None:
        kwargs['event_date'] = event_date
    if event_time is not None:
        kwargs['event_time'] = event_time
    return update_event(event_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_event(event_id):
    """Delete an event from the LMS system.
    
    Args:
        event_id: The ID of the event to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete events", "status": "failed"}
    return delete_event(event_id)


@tool
@readable_result
@jwt_required()
def create_section(name, teacher_name):
    """Create a new section in the LMS system.
    
    Args:
        name: The name of the section
        teacher_name: Name of the teacher for the section
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create sections", "status": "failed"}
    
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return {"message": "Teacher not found", "status": "failed"}
    return add_section(name, teacher.id)


@tool
@readable_result
@jwt_required()
def get_section(section_id):
    """Retrieve a specific section by its ID. Use this when users ask about a specific section.
    
    Args:
        section_id: The ID of the section to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_section_by_id(section_id)


@tool
@readable_result
@jwt_required()
def get_sections():
    """Retrieve all sections from the LMS system. Use this when users ask about sections."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_sections()


@tool
@readable_result
@jwt_required()
def update_section(section_id, name=None, teacher_name=None):
    """Update an existing section.
    
    Args:
        section_id: The ID of the section to update
        name: New name (optional)
        teacher_name: New teacher name (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update sections", "status": "failed"}
    
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if teacher_name is not None:
        teacher = Teacher.query.filter_by(name=teacher_name).first()
        if not teacher:
            return {"message": "Teacher not found", "status": "failed"}
        kwargs['teacher_id'] = teacher.id
    return edit_section(section_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_section(section_id):
    """Delete a section from the LMS system.
    
    Args:
        section_id: The ID of the section to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete sections", "status": "failed"}
    return delete_section(section_id)


@tool
@readable_result
@jwt_required()
def create_student(name, username, section_name, password, email):
    """Create a new student in the LMS system.
    
    Args:
        name: The name of the student
        username: Username for the student
        section_name: Name of the section
        password: Password for the student
        email: Email of the student
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create students", "status": "failed"}
    
    section = Section.query.filter_by(name=section_name).first()
    if not section:
        return {"message": "Section not found", "status": "failed"}
    return add_students(name, username, section.id, password, email)


@tool
@readable_result
@jwt_required()
def get_students():
    """Retrieve students. Teachers only see the students they teach. Use this when users ask about students."""
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Only admins and teachers can view students")

    return keep_ids(to_tool_result(get_all_students()), allowed_student_ids())


@tool
@readable_result
@jwt_required()
def get_student(student_id):
    """Retrieve a specific student by their ID. Teachers can only view the students they teach.

    Args:
        student_id: The ID of the student to retrieve
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Only admins and teachers can view students")

    if not in_scope(int(student_id), allowed_student_ids()):
        return failed(f"No student with ID {student_id} among the students you can access")
    return get_student_by_id(student_id)


@tool
@readable_result
@jwt_required()
def update_student_tool(student_id, name=None, username=None, section_name=None, email=None):
    """Update an existing student.
    
    Args:
        student_id: The ID of the student to update
        name: New name (optional)
        username: New username (optional)
        section_name: New section name (optional)
        email: New email (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update students", "status": "failed"}
    
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if username is not None:
        kwargs['username'] = username
    if section_name is not None:
        section = Section.query.filter_by(name=section_name).first()
        if not section:
            return {"message": "Section not found", "status": "failed"}
        kwargs['section_id'] = section.id
    if email is not None:
        kwargs['email'] = email
    return update_student(student_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_student(student_id):
    """Delete a student from the LMS system.
    
    Args:
        student_id: The ID of the student to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete students", "status": "failed"}
    
    return delete_student(student_id)


@tool
@readable_result
@jwt_required()
def create_course(name, description, course_code, teacher_name, created_at=None):
    """Create a new course in the LMS system.
    
    Args:
        name: The name of the course
        description: Description of the course
        course_code: Code for the course
        teacher_name: Name of the teacher
        created_at: Creation timestamp (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create courses", "status": "failed"}
    
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return {"message": "Teacher not found", "status": "failed"}
    return add_course(name, description, course_code, teacher.id, created_at)


@tool
@readable_result
@jwt_required()
def get_courses():
    """Retrieve all courses from the LMS system. Use this when users ask about courses."""
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_courses()


@tool
@readable_result
@jwt_required()
def get_course(course_id):
    """Retrieve a specific course by its ID. Use this when users ask about a specific course.
    
    Args:
        course_id: The ID of the course to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    return get_course_by_id(course_id)


@tool
@readable_result
@jwt_required()
def update_course_tool(course_id, name=None, description=None, course_code=None, teacher_name=None):
    """Update an existing course.
    
    Args:
        course_id: The ID of the course to update
        name: New name (optional)
        description: New description (optional)
        course_code: New course code (optional)
        teacher_name: New teacher name (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update courses", "status": "failed"}
    
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if description is not None:
        kwargs['description'] = description
    if course_code is not None:
        kwargs['course_code'] = course_code
    if teacher_name is not None:
        teacher = Teacher.query.filter_by(name=teacher_name).first()
        if not teacher:
            return {"message": "Teacher not found", "status": "failed"}
        kwargs['teacher_id'] = teacher.id
    return update_course(course_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_course(course_id):
    """Delete a course from the LMS system.
    
    Args:
        course_id: The ID of the course to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete courses", "status": "failed"}
    return delete_course(course_id)


@tool
@readable_result
@jwt_required()
def enroll_student_tool(course_name, enrollment_date, student_name=None, status='active', grade=None, student_id=None):
    """Enroll a student in a course.
    
    Args:
        student_name: The name of the student
        course_name: The name of the course
        enrollment_date: Date of enrollment
        status: Enrollment status, defaults to 'active'
        grade: Grade (optional)
        student_id: The student's ID, only needed when several students share the name
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can enroll students", "status": "failed"}
    
    student, error = resolve_student(student_name, student_id)
    if error:
        return error
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        return {"message": "Course not found", "status": "failed"}
    return enroll_student(student.id, course.id, enrollment_date, status, grade)


@tool
@readable_result
@jwt_required()
def get_enrollments():
    """Retrieve all enrollments from the LMS system. Use this when users ask about enrollments."""
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can view enrollments", "status": "failed"}
    
    return get_all_enrollments()


@tool
@readable_result
@jwt_required()
def get_enrollments_by_student_tool(student_name=None, student_id=None):
    """Retrieve enrollments for a specific student.
    
    Args:
        student_name: The name of the student
        student_id: The student's ID, only needed when several students share the name
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can view enrollments", "status": "failed"}
    
    student, error = resolve_student(student_name, student_id)
    if error:
        return error
    return get_enrollments_by_student(student.id)


@tool
@readable_result
@jwt_required()
def get_enrollments_by_course_tool(course_name):
    """Retrieve enrollments for a specific course.
    
    Args:
        course_name: The name of the course
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can view enrollments", "status": "failed"}
    
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        return {"message": "Course not found", "status": "failed"}
    return get_enrollments_by_course(course.id)


@tool
@readable_result
@jwt_required()
def update_enrollment_tool(enrollment_id, status=None, grade=None):
    """Update an existing enrollment.
    
    Args:
        enrollment_id: The ID of the enrollment to update
        status: New status (optional)
        grade: New grade (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update enrollments", "status": "failed"}
    
    kwargs = {}
    if status is not None:
        kwargs['status'] = status
    if grade is not None:
        kwargs['grade'] = grade
    return update_enrollment(enrollment_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_enrollment(enrollment_id):
    """Delete an enrollment from the LMS system.
    
    Args:
        enrollment_id: The ID of the enrollment to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete enrollments", "status": "failed"}
    
    return delete_enrollment(enrollment_id)


@tool
@readable_result
@jwt_required()
def add_result_tool(total_marks, obtained_marks, exam_type, student_name=None, subject_name=None, remarks=None, student_id=None, subject_id=None):
    """Add an exam result for one of your students in a subject you teach.
    If the tool says several students or subjects share a name, ask the user which one and call again with student_id or subject_id.

    Args:
        total_marks: Total marks for the exam
        obtained_marks: Marks obtained by the student
        exam_type: Type of the exam: 'midterm', 'final', 'quiz' or 'assignment'
        student_name: The name of the student
        subject_name: The name of the subject
        remarks: Additional remarks (optional)
        student_id: The student's ID, only needed when several students share the name
        subject_id: The subject's ID, only needed when several subjects share the name
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can add results")

    subject, error = resolve_subject(subject_name, subject_id)
    if error:
        return error
    student, error = resolve_student(student_name, student_id)
    if error:
        return error
    return add_result(subject.id, student.id, total_marks, obtained_marks, exam_type, remarks)


def _result_in_scope(result_id):
    result = Result.query.get(int(result_id))
    return result is not None and in_scope(result.subject_id, allowed_subject_ids())


@tool
@readable_result
@jwt_required()
def get_result(result_id):
    """Retrieve a specific result by its ID. Teachers can only view results in subjects they teach.

    Args:
        result_id: The ID of the result to retrieve
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    if not _result_in_scope(result_id):
        return failed(f"No result with ID {result_id} in the subjects you can access")
    return get_result_by_id(result_id)


@tool
@readable_result
@jwt_required()
def get_results():
    """Retrieve results. Teachers only see results in subjects they teach. Use this when users ask about results."""
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    result = to_tool_result(get_all_results())
    subject_ids = allowed_subject_ids()
    if subject_ids is not None:
        allowed = {r.id for r in Result.query.filter(Result.subject_id.in_(subject_ids)).all()}
        result = keep_ids(result, allowed)
    return result


@tool
@readable_result
@jwt_required()
def update_result(result_id, obtained_marks=None, remarks=None):
    """Update a result in a subject you teach.

    Args:
        result_id: The ID of the result to update
        obtained_marks: New obtained marks (optional)
        remarks: New remarks (optional)
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can update results")

    if not _result_in_scope(result_id):
        return failed(f"No result with ID {result_id} in the subjects you teach")

    kwargs = {}
    if obtained_marks is not None:
        kwargs['obtained_marks'] = obtained_marks
    if remarks is not None:
        kwargs['remarks'] = remarks
    return edit_result(result_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_result(result_id):
    """Delete a result in a subject you teach.

    Args:
        result_id: The ID of the result to delete
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can delete results")

    if not _result_in_scope(result_id):
        return failed(f"No result with ID {result_id} in the subjects you teach")
    return delete_result(result_id)


@tool
@readable_result
@jwt_required()
def create_subject(name, teacher_name, course_name):
    """Create a new subject in the LMS system.
    
    Args:
        name: The name of the subject
        teacher_name: Name of the teacher
        course_name: Name of the course
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create subjects", "status": "failed"}
    
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return {"message": "Teacher not found", "status": "failed"}
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        return {"message": "Course not found", "status": "failed"}
    return add_subject(name, teacher.id, course.id)


@tool
@readable_result
@jwt_required()
def get_subjects():
    """Retrieve all subjects from the LMS system. Use this when users ask about subjects."""
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_subjects()


@tool
@readable_result
@jwt_required()
def get_subject(subject_id):
    """Retrieve a specific subject by its ID. Use this when users ask about a specific subject.
    
    Args:
        subject_id: The ID of the subject to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_subject_by_id(subject_id)


@tool
@readable_result
@jwt_required()
def update_subject_tool(subject_id, name=None, teacher_id=None):
    """Update an existing subject.
    
    Args:
        subject_id: The ID of the subject to update
        name: New name (optional)
        teacher_id: New teacher ID (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update subjects", "status": "failed"}
    
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if teacher_id is not None:
        kwargs['teacher_id'] = teacher_id
    return update_subject(subject_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_subject(subject_id):
    """Delete a subject from the LMS system.
    
    Args:
        subject_id: The ID of the subject to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete subjects", "status": "failed"}
    
    return delete_subject(subject_id)


@tool
@readable_result
@jwt_required()
def create_teacher(name, username, email, password):
    """Create a new teacher in the LMS system. A teacher does not need a subject;
    assign subjects afterwards with create_subject.
    
    Args:
        name: The name of the teacher
        username: Username for the teacher
        email: Email of the teacher
        password: Initial password for the teacher (it is hashed before saving)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create teachers", "status": "failed"}

    return add_teacher(name, username, email, password)


@tool
@readable_result
@jwt_required()
def get_teachers():
    """Retrieve all teachers from the LMS system. Use this when users ask about teachers."""
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_teachers()


@tool
@readable_result
@jwt_required()
def get_teacher(teacher_id):
    """Retrieve a specific teacher by their ID. Use this when users ask about a specific teacher.
    
    Args:
        teacher_id: The ID of the teacher to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    return get_teacher_by_id(teacher_id)


@tool
@readable_result
@jwt_required()
def update_teacher_tool(teacher_id, name=None, username=None, email=None):
    """Update an existing teacher. To change which teacher teaches a subject,
    use update_subject_tool instead.
    
    Args:
        teacher_id: The ID of the teacher to update
        name: New name (optional)
        username: New username (optional)
        email: New email (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update teachers", "status": "failed"}
    
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if username is not None:
        kwargs['username'] = username
    if email is not None:
        kwargs['email'] = email
    return update_teacher(teacher_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_teacher(teacher_id):
    """Delete a teacher from the LMS system.
    
    Args:
        teacher_id: The ID of the teacher to delete
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can delete teachers", "status": "failed"}
    
    return delete_teacher(teacher_id)


@tool
@readable_result
@jwt_required()
def create_assignment(title, description, due_date, total_marks, subject_name=None, subject_id=None):
    """Create a new assignment in a subject you teach.

    Args:
        title: The title of the assignment
        description: Description of the assignment
        due_date: Due date for the assignment (YYYY-MM-DD)
        total_marks: Total marks for the assignment
        subject_name: Name of the subject
        subject_id: The subject's ID, only needed when several subjects share the name
    """
    role, teacher_id = current_user()
    if role != "teacher":
        return failed("Only teachers can create assignments")

    subject, error = resolve_subject(subject_name, subject_id)
    if error:
        return error
    return add_assignment(title, description, teacher_id, due_date, subject.id, total_marks)


@tool
@readable_result
@jwt_required()
def get_assignment(assignment_id):
    """Retrieve a specific assignment by its ID. Teachers can only view their own assignments.

    Args:
        assignment_id: The ID of the assignment to retrieve
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    if not in_scope(int(assignment_id), allowed_assignment_ids()):
        return failed(f"No assignment with ID {assignment_id} among your assignments")
    return get_assignment_by_id(assignment_id)


@tool
@readable_result
@jwt_required()
def get_assignments():
    """Retrieve assignments. Teachers only see their own assignments. Use this when users ask about assignments."""
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    return keep_ids(to_tool_result(get_all_assignments()), allowed_assignment_ids())


@tool
@readable_result
@jwt_required()
def update_assignment(assignment_id, title=None, description=None, due_date=None, total_marks=None):
    """Update one of your own assignments.

    Args:
        assignment_id: The ID of the assignment to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        total_marks: New total marks (optional)
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can update assignments")

    if not in_scope(int(assignment_id), allowed_assignment_ids()):
        return failed(f"No assignment with ID {assignment_id} among your assignments")

    kwargs = {}
    if title is not None:
        kwargs['title'] = title
    if description is not None:
        kwargs['description'] = description
    if due_date is not None:
        kwargs['due_date'] = due_date
    if total_marks is not None:
        kwargs['total_marks'] = total_marks
    return edit_assignment(assignment_id, **kwargs)


@tool
@readable_result
@jwt_required()
def remove_assignment(assignment_id):
    """Delete one of your own assignments.

    Args:
        assignment_id: The ID of the assignment to delete
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can delete assignments")

    if not in_scope(int(assignment_id), allowed_assignment_ids()):
        return failed(f"No assignment with ID {assignment_id} among your assignments")
    return delete_assignment(assignment_id)


def _submissions_in_scope(result):
    """Teachers only see submissions to their own assignments."""
    assignment_ids = allowed_assignment_ids()
    if assignment_ids is None:
        return result
    allowed = {s.id for s in AssignmentSubmission.query.filter(
        AssignmentSubmission.assignment_id.in_(assignment_ids)).all()} if assignment_ids else set()
    return keep_ids(result, allowed)


@tool
@readable_result
@jwt_required()
def get_submissions_by_student_tool(student_name=None, student_id=None):
    """Retrieve assignment submissions for one student. Teachers only see submissions to their own assignments.

    Args:
        student_name: The name of the student
        student_id: The student's ID, only needed when several students share the name
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    student, error = resolve_student(student_name, student_id)
    if error:
        return error
    return _submissions_in_scope(to_tool_result(get_submissions_by_student(student.id)))


@tool
@readable_result
@jwt_required()
def get_submissions_by_assignment_tool(assignment_id):
    """Retrieve all submissions for one of your assignments.

    Args:
        assignment_id: The ID of the assignment
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    if not in_scope(int(assignment_id), allowed_assignment_ids()):
        return failed(f"No assignment with ID {assignment_id} among your assignments")
    return get_submissions_by_assignment(assignment_id)


@tool
@readable_result
@jwt_required()
def update_submission_tool(submission_id, feedback=None, marks=None, marks_obtained=None):
    """Grade a submission to one of your assignments: set marks and/or feedback.

    Args:
        submission_id: The ID of the submission to update
        feedback: New feedback (optional)
        marks: Marks awarded for the submission (optional)
        marks_obtained: Alternative name for marks (optional, for backward compatibility)
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can update submissions")

    submission = AssignmentSubmission.query.get(int(submission_id))
    if not submission or not in_scope(submission.assignment_id, allowed_assignment_ids()):
        return failed(f"No submission with ID {submission_id} for your assignments")

    kwargs = {}
    if feedback is not None:
        kwargs['feedback'] = feedback
    if marks is not None:
        kwargs['marks'] = marks
    elif marks_obtained is not None:
        kwargs['marks'] = marks_obtained
    return update_submission(submission_id, **kwargs)


def _attendance_for_student(student_id, limit_to_my_subjects=True):
    """A student's attendance. For teachers, limited to the subjects they teach."""
    result = to_tool_result(get_attendance_by_student(student_id))
    # The service answers "Student not found" when there are simply no records.
    if isinstance(result, dict) and result.get("message") == "Student not found":
        return {"status": "success", "count": 0, "data": []}
    subject_ids = allowed_subject_ids() if limit_to_my_subjects else None
    if subject_ids is not None:
        allowed = {a.id for a in Attendance.query.filter(Attendance.student_id == student_id,
                                                         Attendance.subject_id.in_(subject_ids)).all()}
        result = keep_ids(result, allowed)
    return result


@tool
@readable_result
@jwt_required()
def mark_attendance(status, student_name=None, subject_name=None, student_id=None, subject_id=None):
    """Mark attendance for one of your students in a subject you teach.
    If the tool says several students or subjects share a name, ask the user which one and call again with student_id or subject_id.

    Args:
        status: Attendance status: 'present', 'absent' or 'late'
        student_name: The name of the student
        subject_name: The name of the subject
        student_id: The student's ID, only needed when several students share the name
        subject_id: The subject's ID, only needed when several subjects share the name
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can mark attendance")

    subject, error = resolve_subject(subject_name, subject_id)
    if error:
        return error
    student, error = resolve_student(student_name, student_id)
    if error:
        return error
    return mark_attend(student.id, subject.id, status)


@tool
@readable_result
@jwt_required()
def get_attendance_by_student_tool(student_name=None, student_id=None):
    """Retrieve attendance records for one student. Teachers only see records in subjects they teach.

    Args:
        student_name: The name of the student
        student_id: The student's ID, only needed when several students share the name
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    student, error = resolve_student(student_name, student_id)
    if error:
        return error
    return _attendance_for_student(student.id)


@tool
@readable_result
@jwt_required()
def get_attendance_by_subject_tool(subject_name=None, subject_id=None):
    """Retrieve attendance records for a subject you teach.

    Args:
        subject_name: The name of the subject
        subject_id: The subject's ID, only needed when several subjects share the name
    """
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    subject, error = resolve_subject(subject_name, subject_id)
    if error:
        return error
    return get_attendance_by_subject(subject.id)


@tool
@readable_result
@jwt_required()
def get_all_attendance_tool():
    """Retrieve attendance records. Teachers only see records in subjects they teach."""
    role, _ = current_user()
    if role not in ["admin", "teacher"]:
        return failed("Unauthorized access")

    result = to_tool_result(get_all_attendance())
    subject_ids = allowed_subject_ids()
    if subject_ids is not None:
        allowed = {a.id for a in Attendance.query.filter(Attendance.subject_id.in_(subject_ids)).all()}
        result = keep_ids(result, allowed)
    return result


def _latest_attendance(student_name, subject_name, student_id, subject_id):
    subject, error = resolve_subject(subject_name, subject_id)
    if error:
        return None, error
    student, error = resolve_student(student_name, student_id)
    if error:
        return None, error
    record = (Attendance.query.filter_by(student_id=student.id, subject_id=subject.id)
              .order_by(Attendance.mark_at.desc()).first())
    if not record:
        return None, failed("Attendance record not found for this student and subject")
    return record, None


@tool
@readable_result
@jwt_required()
def update_attendance_tool(status, student_name=None, subject_name=None, student_id=None, subject_id=None):
    """Change the status of a student's most recent attendance record in a subject you teach.

    Args:
        status: New status: 'present', 'absent' or 'late'
        student_name: The name of the student
        subject_name: The name of the subject
        student_id: The student's ID, only needed when several students share the name
        subject_id: The subject's ID, only needed when several subjects share the name
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can update attendance")

    record, error = _latest_attendance(student_name, subject_name, student_id, subject_id)
    if error:
        return error
    return update_attendance(record.id, status=status)


@tool
@readable_result
@jwt_required()
def remove_attendance(student_name=None, subject_name=None, student_id=None, subject_id=None):
    """Delete a student's most recent attendance record in a subject you teach.

    Args:
        student_name: The name of the student
        subject_name: The name of the subject
        student_id: The student's ID, only needed when several students share the name
        subject_id: The subject's ID, only needed when several subjects share the name
    """
    role, _ = current_user()
    if role != "teacher":
        return failed("Only teachers can delete attendance records")

    record, error = _latest_attendance(student_name, subject_name, student_id, subject_id)
    if error:
        return error
    return delete_attendance(record.id)



# --- Student tools: always scoped to the logged-in student --------------------
# The student's ID comes from their JWT, never from the model, so a student can
# only ever see their own records.

@tool
@readable_result
@jwt_required()
def get_my_attendance():
    """Get the logged-in student's own attendance records. Use this when a student asks about their attendance."""
    role, student_id = current_user()
    if role != "student":
        return failed("Only students can use this tool")
    # The student ID comes from the JWT, so no further filtering is needed.
    return _attendance_for_student(student_id, limit_to_my_subjects=False)


@tool
@readable_result
@jwt_required()
def get_my_results():
    """Get the logged-in student's own exam results and grades. Use this when a student asks about their results, marks or grades."""
    token = get_jwt()
    if token.get("role") != "student":
        return {"message": "Only students can use this tool", "status": "failed"}
    return get_results_by_student(int(get_jwt_identity()))


@tool
@readable_result
@jwt_required()
def get_my_submissions():
    """Get the logged-in student's own assignment submissions, including marks and feedback. Use this when a student asks about their submissions."""
    token = get_jwt()
    if token.get("role") != "student":
        return {"message": "Only students can use this tool", "status": "failed"}
    return get_submissions_by_student(int(get_jwt_identity()))
