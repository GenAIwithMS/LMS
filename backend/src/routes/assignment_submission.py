from src.services import submit_assignment,get_submissions_by_assignment,get_submissions_by_student,update_submission,delete_submission,get_submission_file_path
from flask import Blueprint, request, jsonify, send_file
from src.services.save_retry import save_with_retry
from src.schemas import UpdateAssignmentSubmissionSchema
from src.models import AssignmentSubmission
from src.services.access import teacher_owns_assignment, get_teacher_assignment_ids, get_student_assignment_ids, filter_response_by_ids
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required,get_jwt_identity, get_jwt
import logging
import os

# Submissions are checked by teachers. A student sees only their own submissions,
# a teacher only the submissions to their own assignments. The admin has no access.

logger = logging.getLogger(__name__)

assignment_submission_bp = Blueprint("assignment_submission", __name__)

@assignment_submission_bp.route("/api/submit/assignment", methods=["POST"])
@jwt_required()
def submit_assign():
    token = get_jwt()
    if token["role"] != "student":
        return jsonify({"message": "Only students can submit assignments", "status": "failed"}), 403
    
    assignment_id_str = request.form.get("assignment_id")
    submission_text = request.form.get("submission_text")
    submission_file = request.files.get("submission_file")
    
    if not assignment_id_str:
        return jsonify({"message": "Assignment ID is required", "status": "error"}), 400
    
    try:
        assignment_id = int(assignment_id_str)
    except ValueError:
        return jsonify({"message": "Invalid Assignment ID format", "status": "error"}), 400
    
    if not submission_text and not submission_file:
        return jsonify({"message": "Either submission text or a file is required", "status": "error"}), 400
    
    student_id = int(get_jwt_identity())

    # A student can only submit to assignments from teachers who teach them
    if assignment_id not in get_student_assignment_ids(student_id):
        return jsonify({"message": "Assignment not found", "status": "failed"}), 404
    
    def submit_once():
        # A retry reads the uploaded file again from the start
        if submission_file:
            submission_file.stream.seek(0)
        return submit_assignment(student_id, assignment_id, submission_text, submission_file)

    result = save_with_retry(submit_once)
    return result

@assignment_submission_bp.route("/api/get/submissions/by/student", methods=["GET"])
@jwt_required()
def get_submissions_student():
    token = get_jwt()
    user_role = token["role"]
    user_id = int(get_jwt_identity())
    
    if user_role not in ["student", "teacher"]:
        return jsonify({
            "message": "Only teachers and students can view submissions",
            "status": "failed"
        }), 403

    student_id = request.args.get("id", type=int)
    if not student_id:
        if user_role == "student":
            student_id = user_id
        else:
            return jsonify({
                "message": "Student ID is required",
                "status": "error"
            }), 400
    
    if user_role == "student" and student_id != user_id:
        return jsonify({
            "message": "You can only view your own submissions",
            "status": "failed"
        }), 403

    result = get_submissions_by_student(student_id)

    # A teacher only sees this student's submissions to their own assignments
    if user_role == "teacher":
        allowed_ids = []
        for assignment_id in get_teacher_assignment_ids(user_id):
            submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=student_id).all()
            for submission in submissions:
                allowed_ids.append(submission.id)
        result = filter_response_by_ids(result, allowed_ids)

    return result

@assignment_submission_bp.route("/api/get/submissions/by/assignment", methods=["GET"])
@jwt_required()
def get_submissions_assignment():
    token = get_jwt()
    user_role = token["role"]
    user_id = int(get_jwt_identity())

    # Only the assignment's teacher can see all its submissions
    if user_role != "teacher":
        return jsonify({
            "message": "Only teachers can view all submissions for an assignment",
            "status": "failed"
        }), 403

    try:
        assignment_id = request.args.get("id", type=int)
        if not assignment_id:
            return jsonify({
                "message": "Assignment ID is required",
                "status": "error"
            }), 400

        if not teacher_owns_assignment(user_id, assignment_id):
            return jsonify({
                "message": "You can only view submissions for your own assignments",
                "status": "failed"
            }), 403

        result = get_submissions_by_assignment(assignment_id)
        return result
    except Exception:
        # Full details go to the server log; the browser gets a plain message
        logger.exception("Could not load the submissions of an assignment")
        return jsonify({
            "message": "Could not load the submissions. Please try again.",
            "status": "error",
            "data": []
        }), 500

def format_number(value):
    """10.00 -> "10", 7.50 -> "7.5"."""
    if value is None:
        return ""
    text = str(value)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@assignment_submission_bp.route("/api/update/submission", methods=["PUT"])
@jwt_required()
def update_subm():
    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message": "Only teachers can grade submissions",
            "status": "failed"
        }), 403

    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400

    submission = AssignmentSubmission.query.get(submission_id)
    if not submission:
        return jsonify({
            "message": "Submission not found",
            "status": "error"
        }), 404

    teacher_id = int(get_jwt_identity())
    if not teacher_owns_assignment(teacher_id, submission.assignment_id):
        return jsonify({
            "message": "You can only grade submissions for your own assignments",
            "status": "failed"
        }), 403

    try:
        data = UpdateAssignmentSubmissionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    # A teacher only grades: marks and feedback. The student's work stays as submitted.
    grading = {}
    if "marks" in data:
        # Marks go from 0 up to the assignment's total
        marks = data["marks"]
        total = submission.assignment.total_marks
        if marks is not None:
            if marks < 0 or (total is not None and marks > total):
                total_text = format_number(total)
                return jsonify({
                    "message": f"Marks must be between 0 and {total_text}",
                    "status": "failed"
                }), 400
        grading["marks"] = marks
    if "feedback" in data:
        grading["feedback"] = data["feedback"]

    result = save_with_retry(lambda: update_submission(submission_id, **grading))
    return result

@assignment_submission_bp.route("/api/delete/submission", methods=["DELETE"])
@jwt_required()
def delete_subm():
    token = get_jwt()

    # Students can submit, but never delete a submission
    if token["role"] != "teacher":
        return jsonify({
            "message": "Only teachers can delete submissions",
            "status": "failed"
        }), 403

    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400

    submission = AssignmentSubmission.query.get(submission_id)
    if not submission:
        return jsonify({
            "message": "Submission not found",
            "status": "error"
        }), 404

    teacher_id = int(get_jwt_identity())
    if not teacher_owns_assignment(teacher_id, submission.assignment_id):
        return jsonify({
            "message": "You can only delete submissions for your own assignments",
            "status": "failed"
        }), 403

    result = delete_submission(submission_id)
    return result


@assignment_submission_bp.route("/api/submission/file", methods=["GET"])
@jwt_required()
def download_submission_file():
    """Download a submission's file. Allowed for the student who submitted it
    and the teacher of the assignment."""
    token = get_jwt()
    user_role = token["role"]
    user_id = int(get_jwt_identity())

    if user_role not in ["student", "teacher"]:
        return jsonify({
            "message": "Only teachers and students can download submissions",
            "status": "failed"
        }), 403

    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400

    submission = AssignmentSubmission.query.get(submission_id)
    if not submission:
        return jsonify({
            "message": "Submission not found",
            "status": "error"
        }), 404

    if user_role == "student" and submission.student_id != user_id:
        return jsonify({
            "message": "You can only download your own submissions",
            "status": "failed"
        }), 403

    if user_role == "teacher" and not teacher_owns_assignment(user_id, submission.assignment_id):
        return jsonify({
            "message": "You can only download submissions for your own assignments",
            "status": "failed"
        }), 403

    file_path = get_submission_file_path(submission)
    if not file_path:
        return jsonify({
            "message": "This submission has no file",
            "status": "failed"
        }), 404

    # Saved files are named "<random id>_<original name>"; download with the original name
    download_name = os.path.basename(file_path)
    name_parts = download_name.split("_", 1)
    if len(name_parts) == 2 and len(name_parts[0]) == 32:
        download_name = name_parts[1]

    return send_file(file_path, as_attachment=True, download_name=download_name)