
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
    get_submissions_by_student_tool, get_submissions_by_assignment_tool, update_submission_tool
)

# Domain-specific tool lists
announcement_tools = [create_announcement, get_announcements, get_announcement, update_announcement, remove_announcement]
event_tools = [create_event, get_events, get_event, update_event_tool, remove_event]
section_tools = [create_section, get_sections, get_section, update_section, remove_section]
student_tools_list = [create_student, get_students, get_student, update_student_tool, remove_student]
course_tools = [create_course, get_courses, get_course, update_course_tool, remove_course]
enrollment_tools = [enroll_student_tool, get_enrollments, get_enrollments_by_student_tool, get_enrollments_by_course_tool, update_enrollment_tool, remove_enrollment]
result_tools = [add_result_tool, get_results, get_result, update_result, remove_result]
subject_tools = [create_subject, get_subjects, get_subject, update_subject_tool, remove_subject]
teacher_tools_list = [create_teacher, get_teachers, get_teacher, update_teacher_tool, remove_teacher]
attendance_tools = [mark_attendance, get_attendance_by_student_tool, get_attendance_by_subject_tool, get_all_attendance_tool, update_attendance_tool, remove_attendance]
assignment_tools = [create_assignment, get_assignments, get_assignment, update_assignment, remove_assignment]
submission_tools = [get_submissions_by_student_tool, get_submissions_by_assignment_tool, update_submission_tool]

# Tool sets grouped by domain for parallel processing
TOOL_SETS = {
    "admin": {
        "student": student_tools_list,
        "teacher": teacher_tools_list,
        "course": course_tools,
        "section": section_tools,
        "subject": subject_tools,
        "enrollment": enrollment_tools,
        "event": event_tools,
        "result": [get_results, get_result],
        "assignment": assignment_tools,
        "submission": submission_tools,
        "attendance": attendance_tools,
        "announcement": announcement_tools
    },
    "teacher": {
        "announcement": announcement_tools,
        "assignment": assignment_tools,
        "attendance": attendance_tools,
        "result": result_tools,
        "student": [get_students, get_student],
        "submission": [get_submissions_by_student_tool, get_submissions_by_assignment_tool, update_submission_tool]
    },
    "student": {
        "submission": [get_submissions_by_student_tool],
        "attendance": [get_attendance_by_student_tool],
        "result": [get_result],
        "announcement": [get_announcements, get_announcement]
    }
}

# Dynamically generate flat tool lists from TOOL_SETS for backward compatibility
def _flatten_tools(role_tool_sets):
    """Flatten domain-grouped tools into a single list, removing duplicates."""
    tools = []
    seen = set()
    for domain_tools in role_tool_sets.values():
        for tool in domain_tools:
            tool_id = id(tool)
            if tool_id not in seen:
                seen.add(tool_id)
                tools.append(tool)
    return tools

admin_tools = _flatten_tools(TOOL_SETS["admin"])
teacher_tools = _flatten_tools(TOOL_SETS["teacher"])
student_tools = _flatten_tools(TOOL_SETS["student"])
