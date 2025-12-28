from src.services.result import add_result, get_result_by_id, get_all_results, edit_result, delete_result, get_results_by_student
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from src.schemas.result import ResultSchema,UpdateResultSchema
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from src.models.student import Student
from src.models.subject import Subject
from src.models.result import Result

result_bp = Blueprint("result", __name__)

@result_bp.route("/api/create/result", methods=["POST"])
@jwt_required()
def create_res():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teacher's can add results",
            "status":"failed"
        }),403
     
    try:
        data = ResultSchema().load(request.get_json())

    except ValidationError as e:
        return jsonify(e.messages), 400

    subject_name = data.get("subject_name")
    student_name = data.get("student_name")
    total_marks = data.get("total_marks")
    obtained_marks = data.get("obtained_marks")
    exam_type = data.get("exam_type")
    remarks = data.get("remarks")

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "failed"
        }), 400

    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return jsonify({
            "message": "Student not found",
            "status": "failed"
        }), 400
    
    result = add_result(subject.id, student.id, total_marks, obtained_marks, exam_type, remarks)
    return result

@result_bp.route("/api/get/result", methods=["GET"])
@jwt_required()
def get_res():
    token = get_jwt()
    user_role = token["role"]
    result_id = request.args.get("id", type=int)
    
    if result_id is not None:
        # If specific result ID is requested, check if student can access it
        if user_role == "student":
            user_id = int(get_jwt_identity())
            result_obj = Result.query.get(result_id)
            if not result_obj:
                return jsonify({
                    "message": "Result not found",
                    "status": "error"
                }), 404
            if result_obj.student_id != user_id:
                return jsonify({
                    "message": "You can only view your own results",
                    "status": "failed"
                }), 403
        result = get_result_by_id(result_id)
        return result
    
    # If no ID provided, handle based on role
    if user_role == "student":
        # Students can only view their own results
        user_id = int(get_jwt_identity())
        result = get_results_by_student(user_id)
        return result
    elif user_role == "teacher" or user_role == "admin":
        # Teachers and admins can view all results
        result = get_all_results()
        return result
    else:
        return jsonify({
            "message": "Access denied",
            "status": "failed"
        }), 403

@result_bp.route("/api/update/result", methods=["PUT"])
@jwt_required()
def update_res():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teacher's can update results",
            "status":"failed"
        }),403
    
    result_id = request.args.get("id", type=int)
    if not result_id:
        return jsonify({
            "message": "Result ID is required",
            "status": "error"
        }), 400
    try:
        data = UpdateResultSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    kwargs = {}
    for key, value in data.items():
        if key == 'student_name':
            student = Student.query.filter_by(name=value).first()
            if not student:
                return jsonify({"message": "Student not found", "status": "failed"}), 400
            kwargs['student_id'] = student.id
        elif key == 'subject_name':
            subject = Subject.query.filter_by(name=value).first()
            if not subject:
                return jsonify({"message": "Subject not found", "status": "failed"}), 400
            kwargs['subject_id'] = subject.id
        else:
            kwargs[key] = value

    result = edit_result(result_id, **kwargs)
    return result

@result_bp.route("/api/delete/result", methods=["DELETE"])
@jwt_required()
def delete_res():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teacher's can delete results",
            "status":"failed"
        }),403

    result_id = request.args.get("id", type=int)
    if not result_id:
        return jsonify({
            "message": "Result ID is required",
            "status": "error"
        }), 400

    result = delete_result(result_id)
    return result