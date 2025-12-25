
from src.agent.tools import (
    create_announcement, get_announcements, get_announcement, update_announcement, remove_announcement,
    create_event, get_events, get_event, update_event_tool, remove_event,
    create_section, get_sections, get_section, update_section, remove_section,
    create_student, get_students, get_student, update_student_tool, remove_student,
    create_course, get_courses, get_course, update_course_tool, remove_course,
    enroll_student_tool, get_enrollments, get_enrollments_by_student_tool, get_enrollments_by_course_tool, update_enrollment_tool, remove_enrollment,
    add_result_tool, get_results, get_result, update_result, remove_result,
    create_subject, get_subjects, get_subject, update_subject_tool, remove_subject,
    create_teacher, get_teachers, get_teacher, update_teacher_tool, remove_teacher,
    mark_attendance, get_attendance_by_student_tool, get_attendance_by_subject_tool, get_all_attendance_tool, update_attendance_tool, remove_attendance,
    create_assignment, get_assignments, get_assignment, update_assignment, remove_assignment,
    submit_assignment_tool, get_submissions_by_student_tool, get_submissions_by_assignment_tool, update_submission_tool, remove_submission
)

admin_tools = [
    create_student, get_students, get_student, update_student_tool, remove_student,
    create_teacher, get_teachers, get_teacher, update_teacher_tool, remove_teacher,
    create_course, get_courses, get_course, update_course_tool, remove_course,
    create_section, get_sections, get_section, update_section, remove_section,
    create_subject, get_subjects, get_subject, update_subject_tool, remove_subject,
    enroll_student_tool, get_enrollments, get_enrollments_by_student_tool, get_enrollments_by_course_tool, update_enrollment_tool, remove_enrollment,
    create_event, get_events, get_event, update_event_tool, remove_event,
    get_results, get_result,
    create_assignment, get_assignments, get_assignment, update_assignment, remove_assignment,
    submit_assignment_tool, get_submissions_by_student_tool, get_submissions_by_assignment_tool, update_submission_tool, remove_submission,
    mark_attendance, get_attendance_by_student_tool, get_attendance_by_subject_tool, get_all_attendance_tool, update_attendance_tool, remove_attendance,
    create_announcement, get_announcements, get_announcement, update_announcement, remove_announcement
]

teacher_tools = [
    create_announcement, get_announcements, get_announcement, update_announcement, remove_announcement,
    create_assignment, get_assignments, get_assignment, update_assignment, remove_assignment,
    mark_attendance, get_attendance_by_student_tool, get_attendance_by_subject_tool, get_all_attendance_tool, update_attendance_tool, remove_attendance,
    add_result_tool, get_results, get_result, update_result, remove_result,
    get_students, get_student,
    get_submissions_by_student_tool, get_submissions_by_assignment_tool, update_submission_tool, remove_submission
]

student_tools = [
    submit_assignment_tool,
    get_submissions_by_student_tool,
    get_attendance_by_student_tool,
    get_result,
    get_announcements, get_announcement
]
