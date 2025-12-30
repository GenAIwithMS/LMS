import sys
import os
from flask_jwt_extended import get_jwt_identity, get_jwt,jwt_required
from src.models.subject import Subject
from src.models.student import Student
from src.models.teacher import Teacher
from src.models.course import Course
from src.models.section import Section
from src.models.attendance import Attendance
from src.services.announsment import add_announcement,get_all_announcements,get_announcement_by_title,edit_announcement,delete_announcement
from src.services.event import add_event,get_event_by_id,get_all_events,update_event,delete_event
from src.services.section import add_section,get_section_by_id,get_all_sections,edit_section,delete_section
from src.services.students import add_students,get_all_students,get_student_by_id,update_student,delete_student
from src.services.course import add_course,get_all_courses,get_course_by_id,update_course,delete_course
from src.services.enrollment import enroll_student,get_enrollments_by_course,get_enrollments_by_student,update_enrollment,delete_enrollment,get_all_enrollments
from src.services.result import add_result, get_result_by_id, get_all_results, edit_result, delete_result
from src.services.subject import add_subject, get_all_subjects, get_subject_by_id, delete_subject,update_subject
from src.services.teacher import add_teacher, get_teacher_by_id, update_teacher, delete_teacher, get_all_teachers
from src.services.attendance import mark_attend, get_attendance_by_student,get_attendance_by_subject,get_all_attendance,update_attendance,delete_attendance
from src.services.assignment import add_assignment, get_assignment_by_id,get_all_assignments,edit_assignment,delete_assignment
from src.services.assignment_submission import get_submissions_by_student, get_submissions_by_assignment, update_submission
from langchain.tools import tool

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

@tool
@jwt_required()
def create_announcement(title, content, section_name, target_audience = 'all', created_at = None):
    """Create a new announcement in the LMS system.
    
    Args:
        title: The title of the announcement
        content: The content of the announcement
        section_name: Name of the section for the announcement
        target_audience: Target audience, defaults to 'all'
        created_at: Creation timestamp, optional
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can create announcements", "status": "failed"}

    section = Section.query.filter_by(name=section_name).first()
    if not section:
        return {"message": "Section not found", "status": "failed"}
    
    teacher_id = int(get_jwt_identity())
    add_announcement(title, content, teacher_id, section.id, target_audience, created_at)
    return {"message": "Announcement created successfully", "status": "success"}

@tool
@jwt_required()
def get_announcements():
    """Retrieve all announcements from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_announcements()


@tool
@jwt_required()
def get_announcement(announcement_title):
    """Retrieve a specific announcement by its ID.
    
    Args:
        announcement_id: The ID of the announcement to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_announcement_by_title(announcement_title)


@tool
@jwt_required()
def update_announcement(announcement_title, title=None, content=None, target_audience=None, section_name=None):
    """Update an existing announcement.
    
    Args:
        announcement_title: The title of the announcement to update
        title: New title (optional)
        content: New content (optional)
        target_audience: New target audience (optional)
        section_name: New section name (optional)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return "Only teachers can update announcements"
    
    kwargs = {}
    if title is not None:
        kwargs['title'] = title
    if content is not None:
        kwargs['content'] = content
    if target_audience is not None:
        kwargs['target_audience'] = target_audience
    if section_name is not None:
        section = Section.query.filter_by(name=section_name).first()
        if not section:
            return "Section not found"
        kwargs['section_id'] = section.id
    edit_announcement(announcement_title, **kwargs)
    return "Announcement updated successfully"


@tool
@jwt_required()
def remove_announcement(announcement_title):
    """Delete an announcement from the LMS system.
    
    Args:
        announcement_title: The title of the announcement to delete
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return "Only teachers can delete announcements"
    return delete_announcement(announcement_title)
    
@tool
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
@jwt_required()
def get_event(event_id):
    """Retrieve a specific event by its ID.
    
    Args:
        event_id: The ID of the event to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_event_by_id(event_id)


@tool
@jwt_required()
def get_events():
    """Retrieve all events from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_events()


@tool
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
@jwt_required()
def get_section(section_id):
    """Retrieve a specific section by its ID.
    
    Args:
        section_id: The ID of the section to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_section_by_id(section_id)


@tool
@jwt_required()
def get_sections():
    """Retrieve all sections from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_sections()


@tool
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
@jwt_required()
def get_students():
    """Retrieve all students from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Only admins and teachers can view students", "status": "failed"}
    
    return get_all_students()


@tool
@jwt_required()
def get_student(student_id):
    """Retrieve a specific student by their ID.
    
    Args:
        student_id: The ID of the student to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Only admins and teachers can view students", "status": "failed"}
    
    return get_student_by_id(student_id)


@tool
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
        return "Teacher not found"
    add_course(name, description, course_code, teacher.id, created_at)
    return "Course created successfully"


@tool
@jwt_required()
def get_courses():
    """Retrieve all courses from the LMS system."""
    token = get_jwt()
    if token.get("role") not in "admin":
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_courses()


@tool
@jwt_required()
def get_course(course_id):
    """Retrieve a specific course by its ID.
    
    Args:
        course_id: The ID of the course to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    return get_course_by_id(course_id)


@tool
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
            return "Teacher not found"
        kwargs['teacher_id'] = teacher.id
    update_course(course_id, **kwargs)
    return "Course updated successfully"


@tool
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
@jwt_required()
def enroll_student_tool(student_name, course_name, enrollment_date, status='active', grade=None):
    """Enroll a student in a course.
    
    Args:
        student_name: The name of the student
        course_name: The name of the course
        enrollment_date: Date of enrollment
        status: Enrollment status, defaults to 'active'
        grade: Grade (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can enroll students", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        return {"message": "Course not found", "status": "failed"}
    return enroll_student(student.id, course.id, enrollment_date, status, grade)


@tool
@jwt_required()
def get_enrollments():
    """Retrieve all enrollments from the LMS system."""
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can view enrollments", "status": "failed"}
    
    return get_all_enrollments()


@tool
@jwt_required()
def get_enrollments_by_student_tool(student_name):
    """Retrieve enrollments for a specific student.
    
    Args:
        student_name: The name of the student
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can view enrollments", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    return get_enrollments_by_student(student.id)


@tool
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
@jwt_required()
def add_result_tool(subject_name, student_name, total_marks, obtained_marks, exam_type, remarks=None):
    """Add a result for a student in a subject.
    
    Args:
        subject_name: The name of the subject
        student_name: The name of the student
        total_marks: Total marks for the exam
        obtained_marks: Marks obtained by the student
        exam_type: Type of the exam
        remarks: Additional remarks (optional)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can add results", "status": "failed"}
    
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    return add_result(subject.id, student.id, total_marks, obtained_marks, exam_type, remarks)


@tool
@jwt_required()
def get_result(result_id):
    """Retrieve a specific result by its ID.
    
    Args:
        result_id: The ID of the result to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_result_by_id(result_id)


@tool
@jwt_required()
def get_results():
    """Retrieve all results from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_results()


@tool
@jwt_required()
def update_result(result_id, obtained_marks=None, remarks=None):
    """Update an existing result.
    
    Args:
        result_id: The ID of the result to update
        obtained_marks: New obtained marks (optional)
        remarks: New remarks (optional)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can update results", "status": "failed"}
    
    kwargs = {}
    if obtained_marks is not None:
        kwargs['obtained_marks'] = obtained_marks
    if remarks is not None:
        kwargs['remarks'] = remarks
    return edit_result(result_id, **kwargs)


@tool
@jwt_required()
def remove_result(result_id):
    """Delete a result from the LMS system.
    
    Args:
        result_id: The ID of the result to delete
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can delete results", "status": "failed"}
    return delete_result(result_id)


@tool
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
@jwt_required()
def get_subjects():
    """Retrieve all subjects from the LMS system."""
    token = get_jwt()
    if token.get("role") not in "admin":
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_subjects()


@tool
@jwt_required()
def get_subject(subject_id):
    """Retrieve a specific subject by its ID.
    
    Args:
        subject_id: The ID of the subject to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher", "student"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_subject_by_id(subject_id)


@tool
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
@jwt_required()
def create_teacher(name, subject_name, username, email, password_hash):
    """Create a new teacher in the LMS system.
    
    Args:
        name: The name of the teacher
        subject_name: Name of the subject taught by the teacher
        username: Username for the teacher
        email: Email of the teacher
        password_hash: Hashed password
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can create teachers", "status": "failed"}

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    return add_teacher(name, subject.id, username, email, password_hash)


@tool
@jwt_required()
def get_teachers():
    """Retrieve all teachers from the LMS system."""
    token = get_jwt()
    if token.get("role") not in "admin":
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_teachers()


@tool
@jwt_required()
def get_teacher(teacher_id):
    """Retrieve a specific teacher by their ID.
    
    Args:
        teacher_id: The ID of the teacher to retrieve
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    return get_teacher_by_id(teacher_id)


@tool
@jwt_required()
def update_teacher_tool(teacher_id, name=None, subject=None, username=None, email=None):
    """Update an existing teacher.
    
    Args:
        teacher_id: The ID of the teacher to update
        name: New name (optional)
        subject: New subject (optional)
        username: New username (optional)
        email: New email (optional)
    """
    token = get_jwt()
    if token.get("role") != "admin":
        return {"message": "Only admins can update teachers", "status": "failed"}
    
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if subject is not None:
        kwargs['subject'] = subject
    if username is not None:
        kwargs['username'] = username
    if email is not None:
        kwargs['email'] = email
    return update_teacher(teacher_id, **kwargs)


@tool
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
@jwt_required()
def mark_attendance(student_name, subject_name,status):
    """Mark attendance for a student in a subject.
    
    Args:
        student_name: The name of the student
        subject_name: The name of the subject
        status: Attendance status (present/absent/etc.)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can mark attendance", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    
    return mark_attend(student.id, subject.id,status)


@tool
@jwt_required()
def get_attendance_by_student_tool(student_id):
    """Retrieve attendance records for a specific student.
    
    Args:
        student_id: The ID of the student 
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    if student_id is None:
        raise ValueError("student_id must be provided")
    return get_attendance_by_student(student_id)


@tool
@jwt_required()
def get_attendance_by_subject_tool(subject_name):
    """Retrieve attendance records for a specific subject.
    
    Args:
        subject_name: The name of the subject
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    
    return get_attendance_by_subject(subject.id)


@tool
@jwt_required()
def get_all_attendance_tool():
    """Retrieve all attendance records from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    return get_all_attendance()


@tool
@jwt_required()
def update_attendance_tool(attendance_id, status=None):
    """Update an existing attendance record.
    
    Args:
        attendance_id: The ID of the attendance record to update
        status: New status (optional)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can update attendance", "status": "failed"}
    
    kwargs = {}
    if status is not None:
        kwargs['status'] = status
    return update_attendance(attendance_id, **kwargs)


@tool
@jwt_required()
def remove_attendance(attendance_id):
    """Delete an attendance record from the LMS system.
    
    Args:
        attendance_id: The ID of the attendance record to delete
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can delete attendance records", "status": "failed"}
    return delete_attendance(attendance_id)


@tool
@jwt_required()
def create_assignment(title, description, due_date, subject_name, total_marks):
    """Create a new assignment in the LMS system.
    
    Args:
        title: The title of the assignment
        description: Description of the assignment
        due_date: Due date for the assignment
        subject_name: Name of the subject
        total_marks: Total marks for the assignment
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can create assignments", "status": "failed"}
    teacher_id = int(get_jwt_identity())
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    return add_assignment(title, description, teacher_id, due_date, subject.id, total_marks)


@tool
@jwt_required()
def get_assignment(assignment_id):
    """Retrieve a specific assignment by its ID.
    
    Args:
        assignment_id: The ID of the assignment to retrieve
    """
    return get_assignment_by_id(assignment_id)


@tool
@jwt_required()
def get_assignments():
    """Retrieve all assignments from the LMS system."""

    return get_all_assignments()


@tool
@jwt_required()
def update_assignment(assignment_id, title=None, description=None, due_date=None, total_marks=None):
    """Update an existing assignment.
    
    Args:
        assignment_id: The ID of the assignment to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        total_marks: New total marks (optional)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can update assignments", "status": "failed"}
    
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
@jwt_required()
def remove_assignment(assignment_id):
    """Delete an assignment from the LMS system.
    
    Args:
        assignment_id: The ID of the assignment to delete
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can delete assignments", "status": "failed"}
    
    return delete_assignment(assignment_id)


@tool
@jwt_required()
def get_submissions_by_student_tool(student_id):
    """Retrieve assignment submissions for a specific student.
    
    Args:
        student_id: The ID of the student 
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    if student_id is None:
        raise ValueError("student_id must be provided")
    return get_submissions_by_student(student_id)


@tool
@jwt_required()
def get_submissions_by_assignment_tool(assignment_id):
    """Retrieve assignment submissions for a specific assignment.
    
    Args:
        assignment_id: The ID of the assignment
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_submissions_by_assignment(assignment_id)


@tool
@jwt_required()
def update_submission_tool(submission_id, submission_text=None, feedback=None, marks=None, marks_obtained=None):
    """Update an existing assignment submission.
    
    Args:
        submission_id: The ID of the submission to update
        submission_text: New submission text (optional)
        feedback: New feedback (optional)
        marks: Marks awarded for the submission (optional)
        marks_obtained: Alternative name for marks (optional, for backward compatibility)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can update submissions", "status": "failed"}
    
    kwargs = {}
    if submission_text is not None:
        kwargs['submission_text'] = submission_text
    if feedback is not None:
        kwargs['feedback'] = feedback
    if marks is not None:
        kwargs['marks'] = marks
    elif marks_obtained is not None:
        kwargs['marks'] = marks_obtained  
    return update_submission(submission_id, **kwargs)


@tool
@jwt_required()
def mark_attendance(student_name, subject_name, status):
    """Mark attendance for a student in a subject.
    
    Args:
        student_name: The name of the student
        subject_name: The name of the subject
        status: Attendance status ('present', 'absent', 'late')
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can mark attendance", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    mark_attend(student.id, subject.id, status)
    return {"message": "Attendance marked successfully", "status": "success"}


@tool
@jwt_required()
def get_attendance_by_student_tool(student_name):
    """Retrieve attendance records for a specific student.
    
    Args:
        student_name: The name of the student
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    return get_attendance_by_student(student.id)


@tool
@jwt_required()
def get_attendance_by_subject_tool(subject_name):
    """Retrieve attendance records for a specific subject.
    
    Args:
        subject_name: The name of the subject
    """
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    return get_attendance_by_subject(subject.id)


@tool
@jwt_required()
def get_all_attendance_tool():
    """Retrieve all attendance records from the LMS system."""
    token = get_jwt()
    if token.get("role") not in ["admin", "teacher"]:
        return {"message": "Unauthorized access", "status": "failed"}
    
    return get_all_attendance()


@tool
@jwt_required()
def update_attendance_tool(student_name, subject_name, status=None):
    """Update an existing attendance record.
    
    Args:
        student_name: The name of the student
        subject_name: The name of the subject
        status: New status ('present', 'absent', 'late') (optional)
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can update attendance", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    attendance_record = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id).order_by(Attendance.mark_at.desc()).first()
    if not attendance_record:
        return {"message": "Attendance record not found for this student and subject", "status": "failed"}
    kwargs = {}
    if status is not None:
        kwargs['status'] = status
    update_attendance(attendance_record.id, **kwargs)
    return {"message": "Attendance record updated successfully", "status": "success"}


@tool
@jwt_required()
def remove_attendance(student_name, subject_name):
    """Delete an attendance record from the LMS system.
    
    Args:
        student_name: The name of the student
        subject_name: The name of the subject
    """
    token = get_jwt()
    if token.get("role") != "teacher":
        return {"message": "Only teachers can delete attendance records", "status": "failed"}
    
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return {"message": "Student not found", "status": "failed"}
    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return {"message": "Subject not found", "status": "failed"}
    attendance_record = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id).order_by(Attendance.mark_at.desc()).first()
    if not attendance_record:
        return "Attendance record not found for this student and subject"
    delete_attendance(attendance_record.id)
    return "Attendance record deleted successfully"

