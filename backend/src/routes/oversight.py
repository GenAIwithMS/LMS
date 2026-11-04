from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from src.db import pakistan_time
from src.services.oversight import (search_activity_log, get_log_areas, get_teachers_overview, get_teacher_activity,
                                    get_oversight_dashboard)
from src.services.reports import (attendance_report, results_report, syllabus_report, teachers_report,
                                  low_attendance_report, activity_report)

# Admin oversight: the activity log, each teacher's activity, the oversight dashboard,
# and Excel reports. Only the admin can open any of these.

oversight_bp = Blueprint("oversight", __name__)


def only_admin():
    """An error answer if the user is not the admin, otherwise None."""
    if get_jwt().get("role") != "admin":
        return jsonify({"message": "Only the admin can see this", "status": "failed"}), 403
    return None


def read_date(name):
    """A date from the query string, like ?date_from=2026-11-01. (date or None, error message or None)"""
    text = request.args.get(name)
    if not text:
        return None, None
    try:
        return date.fromisoformat(text), None
    except ValueError:
        return None, f"{name} must look like 2026-11-04"


def read_log_filters():
    """The activity log filters from the query string. (filters, error answer or None)"""
    filters = {
        "name": request.args.get("name"),
        "role": request.args.get("role"),
        "user_id": request.args.get("user_id", type=int),
        "action": request.args.get("action"),
        "area": request.args.get("area"),
        "class_id": request.args.get("class_id", type=int),
        "section_id": request.args.get("section_id", type=int),
    }
    for name in ["date_from", "date_to"]:
        value, problem = read_date(name)
        if problem:
            return None, (jsonify({"message": problem, "status": "failed"}), 400)
        filters[name] = value
    return filters, None


# ---------------- Activity log

@oversight_bp.route("/api/oversight/activity", methods=["GET"])
@jwt_required()
def activity_log():
    error = only_admin()
    if error:
        return error
    filters, error = read_log_filters()
    if error:
        return error

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 200:
        per_page = 50
    return search_activity_log(filters, page, per_page)


@oversight_bp.route("/api/oversight/activity/areas", methods=["GET"])
@jwt_required()
def activity_areas():
    error = only_admin()
    if error:
        return error
    return jsonify(get_log_areas())


# ---------------- Teachers and dashboard

@oversight_bp.route("/api/oversight/teachers", methods=["GET"])
@jwt_required()
def teachers_overview():
    error = only_admin()
    if error:
        return error
    return get_teachers_overview()


@oversight_bp.route("/api/oversight/teachers/<int:teacher_id>", methods=["GET"])
@jwt_required()
def teacher_activity(teacher_id):
    error = only_admin()
    if error:
        return error
    return get_teacher_activity(teacher_id)


@oversight_bp.route("/api/oversight/dashboard", methods=["GET"])
@jwt_required()
def oversight_dashboard():
    error = only_admin()
    if error:
        return error
    return get_oversight_dashboard()


# ---------------- Excel reports

@oversight_bp.route("/api/reports/<name>", methods=["GET"])
@jwt_required()
def download_report(name):
    error = only_admin()
    if error:
        return error

    if name == "attendance":
        section_id = request.args.get("section_id", type=int)
        if not section_id:
            return jsonify({"message": "Choose a section", "status": "failed"}), 400
        # The month looks like "2026-11"; no month means this month
        today = pakistan_time().date()
        year = today.year
        month = today.month
        month_text = request.args.get("month")
        if month_text:
            try:
                parts = month_text.split("-")
                year = int(parts[0])
                month = int(parts[1])
            except (ValueError, IndexError):
                return jsonify({"message": "Month must look like 2026-11", "status": "failed"}), 400
            if month < 1 or month > 12:
                return jsonify({"message": "Month must look like 2026-11", "status": "failed"}), 400
        return attendance_report(section_id, year, month)

    if name == "results":
        term_id = request.args.get("term_id", type=int)
        section_id = request.args.get("section_id", type=int)
        if not term_id or not section_id:
            return jsonify({"message": "Choose an exam term and a section", "status": "failed"}), 400
        return results_report(term_id, section_id)

    if name == "syllabus":
        return syllabus_report()

    if name == "teachers":
        return teachers_report()

    if name == "low-attendance":
        return low_attendance_report()

    if name == "activity":
        filters, error = read_log_filters()
        if error:
            return error
        return activity_report(filters)

    return jsonify({"message": "Unknown report", "status": "failed"}), 404
