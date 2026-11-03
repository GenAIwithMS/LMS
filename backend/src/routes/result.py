from src.services import add_result, get_result_by_id, get_all_results, edit_result, delete_result, get_results_by_student
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from src.schemas import ResultSchema,UpdateResultSchema
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from src.models import Student,Result,Subject 
from src.services.access import find_teacher_student, find_teacher_student_by_id, find_teacher_subject, get_teacher_subject_ids, filter_response_by_ids


def teacher_can_access_result(teacher_id, result_id):
    """True if the result is in a subject this teacher teaches."""
    result = Result.query.get(result_id)
    if not result:
        return False
    return result.subject_id in get_teacher_subject_ids(teacher_id)

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
    teacher_id = int(get_jwt_identity())

    subject = find_teacher_subject(teacher_id, subject_name)
    if not subject:
        return jsonify({
            "message": "Subject not found among the subjects you teach",
            "status": "failed"
        }), 400

    # Prefer the ID: two students can have the same name
    if data.get("student_id"):
        student = find_teacher_student_by_id(teacher_id, data["student_id"])
    elif student_name:
        student = find_teacher_student(teacher_id, student_name)
    else:
        return jsonify({
            "message": "student_id or student_name is required",
            "status": "failed"
        }), 400

    if not student:
        return jsonify({
            "message": "Student not found among your students",
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
        if user_role == "teacher":
            teacher_id = int(get_jwt_identity())
            if not teacher_can_access_result(teacher_id, result_id):
                return jsonify({
                    "message": "You can only view results in subjects you teach",
                    "status": "failed"
                }), 403
        result = get_result_by_id(result_id)
        return result
    
    if user_role == "student":
        user_id = int(get_jwt_identity())
        result = get_results_by_student(user_id)
        return result
    elif user_role == "teacher":
        # A teacher only sees results in the subjects they teach
        teacher_id = int(get_jwt_identity())
        allowed_ids = []
        for subject_id in get_teacher_subject_ids(teacher_id):
            results = Result.query.filter_by(subject_id=subject_id).all()
            for item in results:
                allowed_ids.append(item.id)
        result = filter_response_by_ids(get_all_results(), allowed_ids)
        return result
    elif user_role == "admin":
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

    teacher_id = int(get_jwt_identity())
    if not teacher_can_access_result(teacher_id, result_id):
        return jsonify({
            "message": "You can only update results in subjects you teach",
            "status": "failed"
        }), 403

    try:
        data = UpdateResultSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    kwargs = {}
    for key, value in data.items():
        if key == 'student_id':
            student = find_teacher_student_by_id(teacher_id, value)
            if not student:
                return jsonify({"message": "Student not found among your students", "status": "failed"}), 400
            kwargs['student_id'] = student.id
        elif key == 'student_name':
            # The ID wins when both are sent
            if 'student_id' in data:
                continue
            student = find_teacher_student(teacher_id, value)
            if not student:
                return jsonify({"message": "Student not found among your students", "status": "failed"}), 400
            kwargs['student_id'] = student.id
        elif key == 'subject_name':
            subject = find_teacher_subject(teacher_id, value)
            if not subject:
                return jsonify({"message": "Subject not found among the subjects you teach", "status": "failed"}), 400
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

    teacher_id = int(get_jwt_identity())
    if not teacher_can_access_result(teacher_id, result_id):
        return jsonify({
            "message": "You can only delete results in subjects you teach",
            "status": "failed"
        }), 403

    result = delete_result(result_id)
    return result