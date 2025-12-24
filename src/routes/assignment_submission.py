from src.services.assignment_submission import submit_assignment,get_submissions_by_assignment,get_submissions_by_student,update_submission,delete_submission
from flask import Blueprint, request, jsonify


assignment_submission_bp = Blueprint("assignment_submission", __name__)

@assignment_submission_bp.route("/api/submit/assignment", methods=["POST"])
def submit_assign():
    data = request.get_json(silent=True)
    if data is None:
        data = request.form
    student_id = data.get("student_id")
    assignment_id = data.get("assignment_id")
    submission_text = data.get("submission_text")
    submission_file = request.files.get("submission_file")
    submitted_at = data.get("submitted_at")
    feedback = data.get("feedback")

    result = submit_assignment(student_id, assignment_id, submission_text, submission_file, submitted_at, feedback)
    return result

@assignment_submission_bp.route("/api/get/submissions/by_student", methods=["GET"])
def get_submissions_student():
    student_id = request.args.get("id", type=int)
    if not student_id:
        return jsonify({
            "message": "Student ID is required",
            "status": "error"
        }), 400

    result = get_submissions_by_student(student_id)
    return result

@assignment_submission_bp.route("/api/get/submissions/by_assignment", methods=["GET"])
def get_submissions_assignment():
    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400

    result = get_submissions_by_assignment(assignment_id)
    return result

@assignment_submission_bp.route("/api/update/submission", methods=["PUT"])
def update_subm():
    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result = update_submission(submission_id, **data)
    return result

@assignment_submission_bp.route("/api/delete/submission", methods=["DELETE"])
def delete_subm():
    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400

    result = delete_submission(submission_id)
    return result