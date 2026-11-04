import logging
from flask import request
from flask_jwt_extended import get_jwt, decode_token
from src.db import db
from src.models import ActivityLog, Section, Subject, Student, ExamPaper, ClassTest


# The activity log: after every change (POST, PUT, DELETE) and every login or logout,
# one row is written saying who did what, when and from where. The admin reads it
# to see what each teacher has been doing.
#
# It is written in one place (after each request), so new routes are logged too;
# give them a readable description in ENDPOINT_LABELS.

logger = logging.getLogger(__name__)

# endpoint: (action, area, description)
ENDPOINT_LABELS = {
    # Login and account
    "auth.login": ("login", "account", "Logged in"),
    "auth.logout": ("logout", "account", "Logged out"),
    "auth.change_my_password": ("update", "account", "Changed their password"),
    "auth.update_my_username": ("update", "account", "Changed their username"),

    # School structure
    "school.create_session": ("create", "school", "Added an academic session"),
    "school.make_session_current": ("update", "school", "Changed the current session"),
    "school.create_section": ("create", "school", "Added a section"),
    "school.update_section": ("update", "school", "Changed a section (name or class incharge)"),
    "school.delete_section": ("delete", "school", "Deleted a section"),
    "school.choose_subject_teacher": ("update", "school", "Changed a subject teacher"),
    "school.create_subject": ("create", "school", "Added a subject"),
    "school.update_subject": ("update", "school", "Renamed a subject"),
    "school.delete_subject": ("delete", "school", "Deleted a subject"),
    "school.create_chapter": ("create", "syllabus", "Added a syllabus chapter"),
    "school.update_chapter": ("update", "syllabus", "Changed a syllabus chapter"),
    "school.delete_chapter": ("delete", "syllabus", "Deleted a syllabus chapter"),

    # Day-to-day teaching
    "teaching.mark_section_attendance": ("update", "attendance", "Marked daily attendance"),
    "teaching.change_chapter_progress": ("update", "syllabus", "Updated syllabus progress"),
    "teaching.write_diary": ("create", "diary", "Wrote the diary"),
    "teaching.remove_diary": ("delete", "diary", "Deleted a diary entry"),
    "teaching.create_class_test": ("create", "class test", "Added a class test"),
    "teaching.update_class_test": ("update", "class test", "Changed a class test"),
    "teaching.enter_class_test_marks": ("update", "class test", "Entered class test marks"),
    "teaching.remove_class_test": ("delete", "class test", "Deleted a class test"),
    "teaching.change_timetable": ("update", "timetable", "Changed the timetable"),

    # Exams
    "exam.create_term": ("create", "exams", "Added an exam term"),
    "exam.update_term": ("update", "exams", "Changed an exam term"),
    "exam.remove_term": ("delete", "exams", "Deleted an exam term"),
    "exam.create_class_papers": ("create", "exams", "Set up exam papers"),
    "exam.update_paper": ("update", "exams", "Changed an exam paper"),
    "exam.remove_paper": ("delete", "exams", "Deleted an exam paper"),
    "exam.upload_question_paper": ("create", "exams", "Uploaded a question paper"),
    "exam.review_question_paper": ("update", "exams", "Reviewed a question paper"),
    "exam.enter_paper_marks": ("update", "exams", "Entered exam marks"),
    "exam.write_remarks": ("update", "exams", "Wrote report card remarks"),
    "exam.promote": ("update", "exams", "Promoted students"),
    "exam.change_grading_scale": ("update", "exams", "Changed the grading scale"),
    "exam.reset_grading_scale": ("update", "exams", "Reset the grading scale"),

    # Assignments and submissions
    "assignment.create_assign": ("create", "assignments", "Added an assignment"),
    "assignment.update_assignment": ("update", "assignments", "Changed an assignment"),
    "assignment.delete_assig": ("delete", "assignments", "Deleted an assignment"),
    "assignment_submission.submit_assign": ("create", "assignments", "Submitted an assignment"),
    "assignment_submission.update_subm": ("update", "assignments", "Graded or changed a submission"),
    "assignment_submission.delete_subm": ("delete", "assignments", "Deleted a submission"),

    # People
    "student.add_student": ("create", "students", "Added a student"),
    "student.update_std": ("update", "students", "Changed a student"),
    "student.delete_std": ("delete", "students", "Deleted a student"),
    "teacher.add_teach": ("create", "teachers", "Added a teacher"),
    "teacher.update_techer": ("update", "teachers", "Changed a teacher"),
    "teacher.del_teacher": ("delete", "teachers", "Deleted a teacher"),

    # Announcements and events
    "announcement.create_announce": ("create", "announcements", "Posted an announcement"),
    "announcement.edit_announce": ("update", "announcements", "Changed an announcement"),
    "announcement.delete_announce": ("delete", "announcements", "Deleted an announcement"),
    "event.create_ev": ("create", "events", "Added an event"),
    "event.update_ev": ("update", "events", "Changed an event"),
    "event.delete_ev": ("delete", "events", "Deleted an event"),

    # Chatbot
    "chatbot.chat": ("create", "chatbot", "Asked the chatbot"),
    "chatbot.confirm_action": ("update", "chatbot", "Confirmed a chatbot action"),
    "chatbot.clear_chat_history": ("delete", "chatbot", "Cleared the chat history"),
}

# Requests that are not worth logging: the browser sends these on its own
NOT_LOGGED = ["auth.logout_tab_closing", "auth.logout_cancel_closing"]


def read_body():
    """The request's JSON body as a dict, or an empty dict."""
    body = request.get_json(silent=True)
    if isinstance(body, dict):
        return body
    return {}


def find_section_and_subject():
    """The section and subject a request was about, when they can be worked out. (section, subject)"""
    view_args = request.view_args or {}
    body = read_body()
    section = None
    subject = None

    section_id = view_args.get("section_id") or body.get("section_id")
    if section_id:
        section = Section.query.get(section_id)

    subject_id = view_args.get("subject_id") or body.get("subject_id")
    if subject_id:
        subject = Subject.query.get(subject_id)

    # Some requests only name a paper, a test or a student
    if view_args.get("paper_id"):
        paper = ExamPaper.query.get(view_args["paper_id"])
        if paper:
            subject = paper.subject
    if view_args.get("test_id"):
        test = ClassTest.query.get(view_args["test_id"])
        if test:
            section = test.section
            subject = test.subject
    if view_args.get("student_id") and not section:
        student = Student.query.get(view_args["student_id"])
        if student:
            section = student.section

    return section, subject


def find_user(endpoint, response):
    """(role, id, name) of whoever made the request."""
    # A login has no token yet; the new token is in the answer
    if endpoint == "auth.login":
        data = response.get_json(silent=True) or {}
        if data.get("token"):
            claims = decode_token(data["token"])
            return claims.get("role"), int(claims["sub"]), claims.get("name")
        # A failed login: keep the email that was tried (never the password)
        return None, None, read_body().get("email")

    try:
        claims = get_jwt()
    except RuntimeError:
        return None, None, None
    if not claims:
        return None, None, None
    return claims.get("role"), int(claims["sub"]), claims.get("name")


def record_activity(response):
    """Write one activity row for this request, if it changed something. Never breaks the request."""
    try:
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return response
        endpoint = request.endpoint
        if not endpoint or endpoint in NOT_LOGGED or not request.path.startswith("/api/"):
            return response

        is_failed_login = endpoint == "auth.login" and response.status_code == 401
        if response.status_code >= 400 and not is_failed_login:
            return response

        if endpoint in ENDPOINT_LABELS:
            action, area, description = ENDPOINT_LABELS[endpoint]
        else:
            action, area, description = ("update", "other", f"{request.method} {request.path}")
        if is_failed_login:
            action = "login_failed"
            description = "Failed to log in (wrong email or password)"

        role, user_id, user_name = find_user(endpoint, response)

        section, subject = find_section_and_subject()
        details = []
        if subject:
            details.append(subject.name)
        if section:
            details.append(section.full_name())
        if len(details) > 0:
            description = description + ": " + ", ".join(details)

        db.session.add(ActivityLog(
            user_role=role,
            user_id=user_id,
            user_name=user_name,
            action=action,
            area=area,
            description=description[:500],
            method=request.method,
            path=request.path[:255],
            ip_address=request.remote_addr,
            status_code=response.status_code,
            section_id=section.id if section else None,
            class_id=section.class_id if section else None
        ))
        db.session.commit()
    except Exception:
        # The log must never stop the real work from being answered
        db.session.rollback()
        logger.exception("Could not write the activity log")
    return response
