from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from marshmallow import ValidationError
from src.db import pakistan_time
from src.models import Student, SyllabusChapter, DiaryEntry, ClassTest
from src.schemas import (DailyAttendanceSchema, ChapterProgressSchema, DiaryEntrySchema, ClassTestSchema,
                         UpdateClassTestSchema, ClassTestMarksSchema, TimetableSlotSchema, TimetableSettingsSchema)
from src.services.access import teacher_teaches, teacher_is_incharge, user_can_view_section, get_teacher_teaching
from src.services.daily_attendance import get_section_register, save_section_register, get_section_month_summary, get_student_daily_attendance
from src.services.syllabus_progress import get_subject_progress, get_section_progress, update_chapter_progress
from src.services.diary import get_section_diary, save_diary_entry, delete_diary_entry
from src.services.class_test import (add_class_test, get_class_tests, get_class_test_marks, save_class_test_marks,
                                     edit_class_test, delete_class_test, get_student_class_tests, test_data)
from src.services.timetable import (get_section_timetable, set_timetable_slot, clear_section_timetable, get_school_draft,
                                    get_timetable_settings, save_timetable_settings, publish_timetable, get_publish_check,
                                    get_published_section_timetable, get_published_teacher_timetable, get_published_info)

# Teaching, day to day:
# - daily attendance, marked by the section's class incharge
# - syllabus progress and the daily diary, written by each subject teacher
# - class tests and their marks, by the subject teacher
# - the weekly timetable, set by the admin
#
# The admin can see everything. A teacher can see the sections they lead or teach in.
# A student can see their own section.

teaching_bp = Blueprint("teaching", __name__)


def current_user():
    """The role and ID of the logged-in user."""
    return get_jwt().get("role"), int(get_jwt_identity())


def read_day(text):
    """A date from the query string like "2026-11-04". No date means today. None if it's not a valid date."""
    if not text:
        return pakistan_time().date()
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def cannot_view_section(section_id):
    """An error answer if the user may not see this section, otherwise None."""
    role, user_id = current_user()
    if not user_can_view_section(role, user_id, section_id):
        return jsonify({"message": "You can't see this section", "status": "failed"}), 403
    return None


# ---------------- Daily attendance

@teaching_bp.route("/api/school/sections/<int:section_id>/attendance", methods=["GET"])
@jwt_required()
def section_attendance(section_id):
    role, user_id = current_user()
    # Students see their own attendance on their own page, not the whole register
    if role == "student" or not user_can_view_section(role, user_id, section_id):
        return jsonify({"message": "You can't see this section's attendance", "status": "failed"}), 403

    day = read_day(request.args.get("date"))
    if not day:
        return jsonify({"message": "Date must look like 2026-11-04", "status": "failed"}), 400
    return get_section_register(section_id, day)


@teaching_bp.route("/api/school/sections/<int:section_id>/attendance", methods=["POST"])
@jwt_required()
def mark_section_attendance(section_id):
    role, user_id = current_user()
    if role != "teacher" or not teacher_is_incharge(user_id, section_id):
        return jsonify({"message": "Only the class incharge of this section can mark its attendance", "status": "failed"}), 403

    try:
        data = DailyAttendanceSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return save_section_register(section_id, data["date"], data["records"], user_id)


@teaching_bp.route("/api/school/sections/<int:section_id>/attendance/summary", methods=["GET"])
@jwt_required()
def section_attendance_summary(section_id):
    role, user_id = current_user()
    if role == "student" or not user_can_view_section(role, user_id, section_id):
        return jsonify({"message": "You can't see this section's attendance", "status": "failed"}), 403

    # The month looks like "2026-11". No month means this month.
    month_text = request.args.get("month")
    today = pakistan_time().date()
    year = today.year
    month = today.month
    if month_text:
        try:
            parts = month_text.split("-")
            year = int(parts[0])
            month = int(parts[1])
        except (ValueError, IndexError):
            return jsonify({"message": "Month must look like 2026-11", "status": "failed"}), 400
        if month < 1 or month > 12:
            return jsonify({"message": "Month must look like 2026-11", "status": "failed"}), 400
    return get_section_month_summary(section_id, year, month)


@teaching_bp.route("/api/school/my-attendance", methods=["GET"])
@jwt_required()
def my_attendance():
    role, user_id = current_user()
    if role != "student":
        return jsonify({"message": "Only students have their own attendance page", "status": "failed"}), 403
    return get_student_daily_attendance(user_id)


# ---------------- Syllabus progress

@teaching_bp.route("/api/school/sections/<int:section_id>/progress", methods=["GET"])
@jwt_required()
def section_progress(section_id):
    error = cannot_view_section(section_id)
    if error:
        return error
    return get_section_progress(section_id)


@teaching_bp.route("/api/school/sections/<int:section_id>/subjects/<int:subject_id>/progress", methods=["GET"])
@jwt_required()
def subject_progress(section_id, subject_id):
    error = cannot_view_section(section_id)
    if error:
        return error
    return get_subject_progress(section_id, subject_id)


@teaching_bp.route("/api/school/sections/<int:section_id>/chapters/<int:chapter_id>/progress", methods=["PUT"])
@jwt_required()
def change_chapter_progress(section_id, chapter_id):
    role, user_id = current_user()
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404
    if role != "teacher" or not teacher_teaches(user_id, section_id, chapter.subject_id):
        return jsonify({"message": "Only the teacher of this subject in this section can update its progress", "status": "failed"}), 403

    try:
        data = ChapterProgressSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return update_chapter_progress(section_id, chapter_id, data, user_id)


# ---------------- Diary

@teaching_bp.route("/api/school/sections/<int:section_id>/diary", methods=["GET"])
@jwt_required()
def section_diary(section_id):
    error = cannot_view_section(section_id)
    if error:
        return error
    day = read_day(request.args.get("date"))
    if not day:
        return jsonify({"message": "Date must look like 2026-11-04", "status": "failed"}), 400
    return get_section_diary(section_id, day)


@teaching_bp.route("/api/school/sections/<int:section_id>/diary", methods=["POST"])
@jwt_required()
def write_diary(section_id):
    role, user_id = current_user()
    try:
        data = DiaryEntrySchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    if role != "teacher" or not teacher_teaches(user_id, section_id, data["subject_id"]):
        return jsonify({"message": "Only the teacher of this subject in this section can write its diary", "status": "failed"}), 403

    classwork = data.get("classwork")
    homework = data.get("homework")
    return save_diary_entry(section_id, data["subject_id"], data["date"], classwork, homework, user_id)


@teaching_bp.route("/api/school/diary/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def remove_diary(entry_id):
    role, user_id = current_user()
    entry = DiaryEntry.query.get(entry_id)
    if not entry:
        return jsonify({"message": "Diary entry not found", "status": "failed"}), 404
    if role != "teacher" or not teacher_teaches(user_id, entry.section_id, entry.subject_id):
        return jsonify({"message": "Only the teacher of this subject in this section can delete its diary", "status": "failed"}), 403
    return delete_diary_entry(entry_id)


# ---------------- Class tests

def can_change_test(test_id):
    """The test, and an error answer if the user may not change it (None when they may)."""
    role, user_id = current_user()
    test = ClassTest.query.get(test_id)
    if not test:
        return None, (jsonify({"message": "Test not found", "status": "failed"}), 404)
    # Whoever teaches the subject in the section now looks after its tests
    if role != "teacher" or not teacher_teaches(user_id, test.section_id, test.subject_id):
        return test, (jsonify({"message": "Only the teacher of this subject in this section can change its tests", "status": "failed"}), 403)
    return test, None


@teaching_bp.route("/api/school/class-tests", methods=["POST"])
@jwt_required()
def create_class_test():
    role, user_id = current_user()
    try:
        data = ClassTestSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    if role != "teacher" or not teacher_teaches(user_id, data["section_id"], data["subject_id"]):
        return jsonify({"message": "You can only add tests for subjects you teach in that section", "status": "failed"}), 403

    return add_class_test(data["section_id"], data["subject_id"], user_id, data["title"], data["date"],
                          data["total_marks"], data.get("chapter_id"))


@teaching_bp.route("/api/school/class-tests", methods=["GET"])
@jwt_required()
def list_class_tests():
    role, user_id = current_user()
    section_id = request.args.get("section_id", type=int)
    subject_id = request.args.get("subject_id", type=int)

    if role == "student":
        return get_student_class_tests(user_id)

    if role == "admin":
        return get_class_tests(section_id, subject_id)

    # A teacher sees the tests of the subjects they teach, in the sections where they teach them
    test_list = []
    for teaching in get_teacher_teaching(user_id):
        if section_id and teaching.section_id != section_id:
            continue
        if subject_id and teaching.subject_id != subject_id:
            continue
        tests = ClassTest.query.filter_by(section_id=teaching.section_id, subject_id=teaching.subject_id).all()
        for test in tests:
            test_list.append(test_data(test))
    test_list.sort(key=lambda item: (item["date"], item["id"]), reverse=True)
    return jsonify(test_list)


@teaching_bp.route("/api/school/class-tests/<int:test_id>", methods=["GET"])
@jwt_required()
def class_test_details(test_id):
    role, user_id = current_user()
    test = ClassTest.query.get(test_id)
    if not test:
        return jsonify({"message": "Test not found", "status": "failed"}), 404

    # The admin, the subject teacher and the class incharge can see everyone's marks
    allowed = False
    if role == "admin":
        allowed = True
    if role == "teacher":
        if teacher_teaches(user_id, test.section_id, test.subject_id) or teacher_is_incharge(user_id, test.section_id):
            allowed = True
    if not allowed:
        return jsonify({"message": "You can't see this test's marks", "status": "failed"}), 403
    return get_class_test_marks(test_id)


@teaching_bp.route("/api/school/class-tests/<int:test_id>", methods=["PUT"])
@jwt_required()
def update_class_test(test_id):
    test, error = can_change_test(test_id)
    if error:
        return error
    try:
        data = UpdateClassTestSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_class_test(test_id, data)


@teaching_bp.route("/api/school/class-tests/<int:test_id>/marks", methods=["PUT"])
@jwt_required()
def enter_class_test_marks(test_id):
    test, error = can_change_test(test_id)
    if error:
        return error
    try:
        data = ClassTestMarksSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return save_class_test_marks(test_id, data["marks"])


@teaching_bp.route("/api/school/class-tests/<int:test_id>", methods=["DELETE"])
@jwt_required()
def remove_class_test(test_id):
    test, error = can_change_test(test_id)
    if error:
        return error
    return delete_class_test(test_id)


# ---------------- Timetable

@teaching_bp.route("/api/school/sections/<int:section_id>/timetable", methods=["GET"])
@jwt_required()
def section_timetable(section_id):
    error = cannot_view_section(section_id)
    if error:
        return error
    # The admin works on the draft; everyone else sees the published timetable
    role, user_id = current_user()
    if role == "admin":
        return get_section_timetable(section_id)
    return get_published_section_timetable(section_id)


@teaching_bp.route("/api/school/sections/<int:section_id>/timetable", methods=["PUT"])
@jwt_required()
def change_timetable(section_id):
    error = only_admin_timetable()
    if error:
        return error
    try:
        data = TimetableSlotSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return set_timetable_slot(section_id, data["day"], data["period"], data["subject_id"])


@teaching_bp.route("/api/school/sections/<int:section_id>/timetable", methods=["DELETE"])
@jwt_required()
def empty_timetable(section_id):
    error = only_admin_timetable()
    if error:
        return error
    return clear_section_timetable(section_id)


@teaching_bp.route("/api/school/my-timetable", methods=["GET"])
@jwt_required()
def my_timetable():
    """The published timetable: a teacher's own week, or a student's section."""
    role, user_id = current_user()
    if role == "teacher":
        return get_published_teacher_timetable(user_id)
    if role == "student":
        student = Student.query.get(user_id)
        if not student:
            return jsonify({"message": "Student not found", "status": "failed"}), 404
        return get_published_section_timetable(student.section_id)
    return jsonify({"message": "Open the Timetable page to see every section", "status": "failed"}), 400


# ---------------- The whole school's timetable (admin), and publishing it

def only_admin_timetable():
    """An error answer if the user is not the admin, otherwise None."""
    role, user_id = current_user()
    if role != "admin":
        return jsonify({"message": "Only the admin can change the timetable", "status": "failed"}), 403
    return None


@teaching_bp.route("/api/timetable/settings", methods=["GET"])
@jwt_required()
def timetable_settings():
    return get_timetable_settings()


@teaching_bp.route("/api/timetable/settings", methods=["PUT"])
@jwt_required()
def change_timetable_settings():
    error = only_admin_timetable()
    if error:
        return error
    try:
        data = TimetableSettingsSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return save_timetable_settings(data["days"], data["periods"])


@teaching_bp.route("/api/timetable/draft", methods=["GET"])
@jwt_required()
def timetable_draft():
    error = only_admin_timetable()
    if error:
        return error
    return get_school_draft()


@teaching_bp.route("/api/timetable/publish-check", methods=["GET"])
@jwt_required()
def timetable_publish_check():
    error = only_admin_timetable()
    if error:
        return error
    return get_publish_check()


@teaching_bp.route("/api/timetable/publish", methods=["POST"])
@jwt_required()
def timetable_publish():
    error = only_admin_timetable()
    if error:
        return error
    return publish_timetable(get_jwt().get("name"))


@teaching_bp.route("/api/timetable/published-info", methods=["GET"])
@jwt_required()
def timetable_published_info():
    return get_published_info()
