from src.services.result import add_result, get_result_by_id, get_all_results, edit_result, delete_result
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from src.schemas.result import ResultSchema

result_bp = Blueprint("result", __name__)

@result_bp.route("/api/create/result", methods=["POST"])
def create_res():
    try:
        data = ResultSchema().load(request.get_json())

    except ValidationError as e:
        return jsonify(e.messages), 400

    subject_id = data.get("subject_id")
    student_id = data.get("student_id")
    total_marks = data.get("total_marks")
    obtained_marks = data.get("obtained_marks")
    exam_type = data.get("exam_type")
    remarks = data.get("remarks")
    
    result = add_result(subject_id, student_id, total_marks, obtained_marks,exam_type, remarks)
    return result

@result_bp.route("/api/get/result", methods=["GET"])
def get_res():
    result_id = request.args.get("id", type=int)
    if result_id is None:
        result = get_all_results()
        return result

    result = get_result_by_id(result_id)
    return result

@result_bp.route("/api/update/result", methods=["PUT"])
def update_res():

    result_id = request.args.get("id", type=int)
    if not result_id:
        return jsonify({
            "message": "Result ID is required",
            "status": "error"
        }), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result = edit_result(result_id, **data)
    return result

@result_bp.route("/api/delete/result", methods=["DELETE"])
def delete_res():

    result_id = request.args.get("id", type=int)
    if not result_id:
        return jsonify({
            "message": "Result ID is required",
            "status": "error"
        }), 400

    result = delete_result(result_id)
    return result