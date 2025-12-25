from src.services.assignment_submission import submit_assignment,get_submissions_by_assignment,get_submissions_by_student,update_submission,delete_submission
from flask import Blueprint, request, jsonify
from src.schemas.assignment_submission import AssignmentSubmissionSchema,UpdateAssignmentSubmissionSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

assignment_submission_bp = Blueprint("assignment_submission", __name__)

@assignment_submission_bp.route("/api/submit/assignment", methods=["POST"])
@jwt_required()
def submit_assign():
    
    try:
        data = AssignmentSubmissionSchema().load(request.form)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    student_id = data.get("student_id")
    assignment_id = data.get("assignment_id")
    submission_text = data.get("submission_text")
    submission_file = request.files.get("submission_file")
    submitted_at = data.get("submitted_at")
    feedback = data.get("feedback")

    result = submit_assignment(student_id, assignment_id, submission_text, submission_file, submitted_at, feedback)
    return result

@assignment_submission_bp.route("/api/get/submissions/by_student", methods=["GET"])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def update_subm():
    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400
    
    try:
        data = UpdateAssignmentSubmissionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    result = update_submission(submission_id, **data)
    return result

@assignment_submission_bp.route("/api/delete/submission", methods=["DELETE"])
@jwt_required()
def delete_subm():
    submission_id = request.args.get("id", type=int)
    if not submission_id:
        return jsonify({
            "message": "Submission ID is required",
            "status": "error"
        }), 400

    result = delete_submission(submission_id)
    return result