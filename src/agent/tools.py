import sys
import os

# Add the project root to Python path so src package can be found
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.services.announsment import add_announcement,get_all_announcements,get_announcement_by_id,edit_announcement,delete_announcement
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
from src.services.assignment_submission import submit_assignment, get_submissions_by_student, get_submissions_by_assignment, update_submission, delete_submission
from langchain.tools import tool


@tool
def create_announcement(title, content, teacher_id, section_id, target_audience='all', created_at=None):
    """Create a new announcement in the LMS system.
    
    Args:
        title: The title of the announcement
        content: The content of the announcement
        teacher_id: ID of the teacher creating the announcement
        section_id: ID of the section for the announcement
        target_audience: Target audience, defaults to 'all'
        created_at: Creation timestamp, optional
    """
    return add_announcement(title, content, teacher_id, section_id, target_audience, created_at)


@tool
def get_announcements():
    """Retrieve all announcements from the LMS system."""
    return get_all_announcements()


@tool
def get_announcement(announcement_id):
    """Retrieve a specific announcement by its ID.
    
    Args:
        announcement_id: The ID of the announcement to retrieve
    """
    return get_announcement_by_id(announcement_id)


@tool
def update_announcement(announcement_id, title=None, content=None, target_audience=None):
    """Update an existing announcement.
    
    Args:
        announcement_id: The ID of the announcement to update
        title: New title (optional)
        content: New content (optional)
        target_audience: New target audience (optional)
    """
    kwargs = {}
    if title is not None:
        kwargs['title'] = title
    if content is not None:
        kwargs['content'] = content
    if target_audience is not None:
        kwargs['target_audience'] = target_audience
    return edit_announcement(announcement_id, **kwargs)


@tool
def remove_announcement(announcement_id):
    """Delete an announcement from the LMS system.
    
    Args:
        announcement_id: The ID of the announcement to delete
    """
    return delete_announcement(announcement_id)


@tool
def create_event(title, description, event_date, event_time, created_at, admin_id):
    """Create a new event in the LMS system.
    
    Args:
        title: The title of the event
        description: Description of the event
        event_date: Date of the event
        event_time: Time of the event
        created_at: Creation timestamp
        admin_id: ID of the admin creating the event
    """
    return add_event(title, description, event_date, event_time, created_at, admin_id)


@tool
def get_event(event_id):
    """Retrieve a specific event by its ID.
    
    Args:
        event_id: The ID of the event to retrieve
    """
    return get_event_by_id(event_id)


@tool
def get_events():
    """Retrieve all events from the LMS system."""
    return get_all_events()


@tool
def update_event_tool(event_id, title=None, description=None, event_date=None, event_time=None):
    """Update an existing event.
    
    Args:
        event_id: The ID of the event to update
        title: New title (optional)
        description: New description (optional)
        event_date: New event date (optional)
        event_time: New event time (optional)
    """
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
def remove_event(event_id):
    """Delete an event from the LMS system.
    
    Args:
        event_id: The ID of the event to delete
    """
    return delete_event(event_id)


@tool
def create_section(name, teacher_id):
    """Create a new section in the LMS system.
    
    Args:
        name: The name of the section
        teacher_id: ID of the teacher for the section
    """
    return add_section(name, teacher_id)


@tool
def get_section(section_id):
    """Retrieve a specific section by its ID.
    
    Args:
        section_id: The ID of the section to retrieve
    """
    return get_section_by_id(section_id)


@tool
def get_sections():
    """Retrieve all sections from the LMS system."""
    return get_all_sections()


@tool
def update_section(section_id, name=None, teacher_id=None):
    """Update an existing section.
    
    Args:
        section_id: The ID of the section to update
        name: New name (optional)
        teacher_id: New teacher ID (optional)
    """
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if teacher_id is not None:
        kwargs['teacher_id'] = teacher_id
    return edit_section(section_id, **kwargs)


@tool
def remove_section(section_id):
    """Delete a section from the LMS system.
    
    Args:
        section_id: The ID of the section to delete
    """
    return delete_section(section_id)


@tool
def create_student(name, username, section, password, email, teacher_id):
    """Create a new student in the LMS system.
    
    Args:
        name: The name of the student
        username: Username for the student
        section: Section of the student
        password: Password for the student
        email: Email of the student
        teacher_id: ID of the teacher
    """
    return add_students(name, username, section, password, email, teacher_id)


@tool
def get_students():
    """Retrieve all students from the LMS system."""
    return get_all_students()


@tool
def get_student(student_id):
    """Retrieve a specific student by their ID.
    
    Args:
        student_id: The ID of the student to retrieve
    """
    return get_student_by_id(student_id)


@tool
def update_student_tool(student_id, name=None, username=None, section=None, email=None):
    """Update an existing student.
    
    Args:
        student_id: The ID of the student to update
        name: New name (optional)
        username: New username (optional)
        section: New section (optional)
        email: New email (optional)
    """
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if username is not None:
        kwargs['username'] = username
    if section is not None:
        kwargs['section'] = section
    if email is not None:
        kwargs['email'] = email
    return update_student(student_id, **kwargs)


@tool
def remove_student(student_id):
    """Delete a student from the LMS system.
    
    Args:
        student_id: The ID of the student to delete
    """
    return delete_student(student_id)


@tool
def create_course(name, description, course_code, teacher_id, created_at=None):
    """Create a new course in the LMS system.
    
    Args:
        name: The name of the course
        description: Description of the course
        course_code: Code for the course
        teacher_id: ID of the teacher
        created_at: Creation timestamp (optional)
    """
    return add_course(name, description, course_code, teacher_id, created_at)


@tool
def get_courses():
    """Retrieve all courses from the LMS system."""
    return get_all_courses()


@tool
def get_course(course_id):
    """Retrieve a specific course by its ID.
    
    Args:
        course_id: The ID of the course to retrieve
    """
    return get_course_by_id(course_id)


@tool
def update_course_tool(course_id, name=None, description=None, course_code=None):
    """Update an existing course.
    
    Args:
        course_id: The ID of the course to update
        name: New name (optional)
        description: New description (optional)
        course_code: New course code (optional)
    """
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if description is not None:
        kwargs['description'] = description
    if course_code is not None:
        kwargs['course_code'] = course_code
    return update_course(course_id, **kwargs)


@tool
def remove_course(course_id):
    """Delete a course from the LMS system.
    
    Args:
        course_id: The ID of the course to delete
    """
    return delete_course(course_id)


@tool
def enroll_student_tool(student_id, course_id, enrollment_date, status='active', grade=None):
    """Enroll a student in a course.
    
    Args:
        student_id: The ID of the student
        course_id: The ID of the course
        enrollment_date: Date of enrollment
        status: Enrollment status, defaults to 'active'
        grade: Grade (optional)
    """
    return enroll_student(student_id, course_id, enrollment_date, status, grade)


@tool
def get_enrollments():
    """Retrieve all enrollments from the LMS system."""
    return get_all_enrollments()


@tool
def get_enrollments_by_student_tool(student_id):
    """Retrieve enrollments for a specific student.
    
    Args:
        student_id: The ID of the student
    """
    return get_enrollments_by_student(student_id)


@tool
def get_enrollments_by_course_tool(course_id):
    """Retrieve enrollments for a specific course.
    
    Args:
        course_id: The ID of the course
    """
    return get_enrollments_by_course(course_id)


@tool
def update_enrollment_tool(enrollment_id, status=None, grade=None):
    """Update an existing enrollment.
    
    Args:
        enrollment_id: The ID of the enrollment to update
        status: New status (optional)
        grade: New grade (optional)
    """
    kwargs = {}
    if status is not None:
        kwargs['status'] = status
    if grade is not None:
        kwargs['grade'] = grade
    return update_enrollment(enrollment_id, **kwargs)


@tool
def remove_enrollment(enrollment_id):
    """Delete an enrollment from the LMS system.
    
    Args:
        enrollment_id: The ID of the enrollment to delete
    """
    return delete_enrollment(enrollment_id)


@tool
def add_result_tool(subject_id, student_id, total_marks, obtained_marks, exam_type, remarks=None):
    """Add a result for a student in a subject.
    
    Args:
        subject_id: The ID of the subject
        student_id: The ID of the student
        total_marks: Total marks for the exam
        obtained_marks: Marks obtained by the student
        exam_type: Type of the exam
        remarks: Additional remarks (optional)
    """
    return add_result(subject_id, student_id, total_marks, obtained_marks, exam_type, remarks)


@tool
def get_result(result_id):
    """Retrieve a specific result by its ID.
    
    Args:
        result_id: The ID of the result to retrieve
    """
    return get_result_by_id(result_id)


@tool
def get_results():
    """Retrieve all results from the LMS system."""
    return get_all_results()


@tool
def update_result(result_id, obtained_marks=None, remarks=None):
    """Update an existing result.
    
    Args:
        result_id: The ID of the result to update
        obtained_marks: New obtained marks (optional)
        remarks: New remarks (optional)
    """
    kwargs = {}
    if obtained_marks is not None:
        kwargs['obtained_marks'] = obtained_marks
    if remarks is not None:
        kwargs['remarks'] = remarks
    return edit_result(result_id, **kwargs)


@tool
def remove_result(result_id):
    """Delete a result from the LMS system.
    
    Args:
        result_id: The ID of the result to delete
    """
    return delete_result(result_id)


@tool
def create_subject(name, teacher_id, course_code=None):
    """Create a new subject in the LMS system.
    
    Args:
        name: The name of the subject
        teacher_id: ID of the teacher
        course_code: Course code (optional)
    """
    return add_subject(name, teacher_id, course_code)


@tool
def get_subjects():
    """Retrieve all subjects from the LMS system."""
    return get_all_subjects()


@tool
def get_subject(subject_id):
    """Retrieve a specific subject by its ID.
    
    Args:
        subject_id: The ID of the subject to retrieve
    """
    return get_subject_by_id(subject_id)


@tool
def update_subject_tool(subject_id, name=None, teacher_id=None, course_code=None):
    """Update an existing subject.
    
    Args:
        subject_id: The ID of the subject to update
        name: New name (optional)
        teacher_id: New teacher ID (optional)
        course_code: New course code (optional)
    """
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if teacher_id is not None:
        kwargs['teacher_id'] = teacher_id
    if course_code is not None:
        kwargs['course_code'] = course_code
    return update_subject(subject_id, **kwargs)


@tool
def remove_subject(subject_id):
    """Delete a subject from the LMS system.
    
    Args:
        subject_id: The ID of the subject to delete
    """
    return delete_subject(subject_id)


@tool
def create_teacher(name, subject, username, email, password_hash, student_id):
    """Create a new teacher in the LMS system.
    
    Args:
        name: The name of the teacher
        subject: Subject taught by the teacher
        username: Username for the teacher
        email: Email of the teacher
        password_hash: Hashed password
        student_id: Associated student ID
    """
    return add_teacher(name, subject, username, email, password_hash, student_id)


@tool
def get_teachers():
    """Retrieve all teachers from the LMS system."""
    return get_all_teachers()


@tool
def get_teacher(teacher_id):
    """Retrieve a specific teacher by their ID.
    
    Args:
        teacher_id: The ID of the teacher to retrieve
    """
    return get_teacher_by_id(teacher_id)


@tool
def update_teacher_tool(teacher_id, name=None, subject=None, username=None, email=None):
    """Update an existing teacher.
    
    Args:
        teacher_id: The ID of the teacher to update
        name: New name (optional)
        subject: New subject (optional)
        username: New username (optional)
        email: New email (optional)
    """
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
def remove_teacher(teacher_id):
    """Delete a teacher from the LMS system.
    
    Args:
        teacher_id: The ID of the teacher to delete
    """
    return delete_teacher(teacher_id)


@tool
def mark_attendance(student_id, subject_id, date, time, status):
    """Mark attendance for a student in a subject.
    
    Args:
        student_id: The ID of the student
        subject_id: The ID of the subject
        date: Date of attendance
        time: Time of attendance
        status: Attendance status (present/absent/etc.)
    """
    return mark_attend(student_id, subject_id, date, time, status)


@tool
def get_attendance_by_student_tool(student_id):
    """Retrieve attendance records for a specific student.
    
    Args:
        student_id: The ID of the student
    """
    return get_attendance_by_student(student_id)


@tool
def get_attendance_by_subject_tool(subject_id):
    """Retrieve attendance records for a specific subject.
    
    Args:
        subject_id: The ID of the subject
    """
    return get_attendance_by_subject(subject_id)


@tool
def get_all_attendance_tool():
    """Retrieve all attendance records from the LMS system."""
    return get_all_attendance()


@tool
def update_attendance_tool(attendance_id, status=None):
    """Update an existing attendance record.
    
    Args:
        attendance_id: The ID of the attendance record to update
        status: New status (optional)
    """
    kwargs = {}
    if status is not None:
        kwargs['status'] = status
    return update_attendance(attendance_id, **kwargs)


@tool
def remove_attendance(attendance_id):
    """Delete an attendance record from the LMS system.
    
    Args:
        attendance_id: The ID of the attendance record to delete
    """
    return delete_attendance(attendance_id)


@tool
def create_assignment(title, description, student_id, due_date, subject_id, total_marks):
    """Create a new assignment in the LMS system.
    
    Args:
        title: The title of the assignment
        description: Description of the assignment
        student_id: ID of the student
        due_date: Due date for the assignment
        subject_id: ID of the subject
        total_marks: Total marks for the assignment
    """
    return add_assignment(title, description, student_id, due_date, subject_id, total_marks)


@tool
def get_assignment(assignment_id):
    """Retrieve a specific assignment by its ID.
    
    Args:
        assignment_id: The ID of the assignment to retrieve
    """
    return get_assignment_by_id(assignment_id)


@tool
def get_assignments():
    """Retrieve all assignments from the LMS system."""
    return get_all_assignments()


@tool
def update_assignment(assignment_id, title=None, description=None, due_date=None, total_marks=None):
    """Update an existing assignment.
    
    Args:
        assignment_id: The ID of the assignment to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        total_marks: New total marks (optional)
    """
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
def remove_assignment(assignment_id):
    """Delete an assignment from the LMS system.
    
    Args:
        assignment_id: The ID of the assignment to delete
    """
    return delete_assignment(assignment_id)


@tool
def submit_assignment_tool(student_id, assignment_id, submission_text=None, submission_file=None, submitted_at=None, feedback=None):
    """Submit an assignment for a student.
    
    Args:
        student_id: The ID of the student
        assignment_id: The ID of the assignment
        submission_text: Text submission (optional)
        submission_file: File submission (optional)
        submitted_at: Submission timestamp (optional)
        feedback: Feedback (optional)
    """
    return submit_assignment(student_id, assignment_id, submission_text, submission_file, submitted_at, feedback)


@tool
def get_submissions_by_student_tool(student_id):
    """Retrieve assignment submissions for a specific student.
    
    Args:
        student_id: The ID of the student
    """
    return get_submissions_by_student(student_id)


@tool
def get_submissions_by_assignment_tool(assignment_id):
    """Retrieve assignment submissions for a specific assignment.
    
    Args:
        assignment_id: The ID of the assignment
    """
    return get_submissions_by_assignment(assignment_id)


@tool
def update_submission_tool(submission_id, submission_text=None, feedback=None):
    """Update an existing assignment submission.
    
    Args:
        submission_id: The ID of the submission to update
        submission_text: New submission text (optional)
        feedback: New feedback (optional)
    """
    kwargs = {}
    if submission_text is not None:
        kwargs['submission_text'] = submission_text
    if feedback is not None:
        kwargs['feedback'] = feedback
    return update_submission(submission_id, **kwargs)


@tool
def remove_submission(submission_id):
    """Delete an assignment submission from the LMS system.
    
    Args:
        submission_id: The ID of the submission to delete
    """
    return delete_submission(submission_id)

