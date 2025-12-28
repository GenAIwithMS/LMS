from src.services.assignment_submission import submit_assignment,get_submissions_by_assignment,get_submissions_by_student,update_submission,delete_submission
from flask import Blueprint, request, jsonify
from src.schemas.assignment_submission import AssignmentSubmissionSchema,UpdateAssignmentSubmissionSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required,get_jwt_identity, get_jwt

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
    
    result = submit_assignment(student_id, assignment_id, submission_text, submission_file)
    return result

@assignment_submission_bp.route("/api/get/submissions/by/student", methods=["GET"])
@jwt_required()
def get_submissions_student():
    token = get_jwt()
    user_role = token["role"]
    user_id = int(get_jwt_identity())
    
    student_id = request.args.get("id", type=int)
    if not student_id:
        # If no ID provided, students can view their own submissions
        if user_role == "student":
            student_id = user_id
        else:
            return jsonify({
                "message": "Student ID is required",
                "status": "error"
            }), 400
    
    # Students can only view their own submissions
    if user_role == "student" and student_id != user_id:
        return jsonify({
            "message": "You can only view your own submissions",
            "status": "failed"
        }), 403

    result = get_submissions_by_student(student_id)
    return result

@assignment_submission_bp.route("/api/get/submissions/by/assignment", methods=["GET"])
@jwt_required()
def get_submissions_assignment():
    try:
        assignment_id = request.args.get("id", type=int)
        if not assignment_id:
            return jsonify({
                "message": "Assignment ID is required",
                "status": "error"
            }), 400

        result = get_submissions_by_assignment(assignment_id)
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_submissions_assignment route: {error_trace}")
        return jsonify({
            "message": f"Error fetching submissions: {str(e)}",
            "status": "error",
            "data": []
        }), 500

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