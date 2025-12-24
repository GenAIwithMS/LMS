from src.services.subject import create_subject, get_all_subjects, get_subject_by_id, delete_subject,update_subject
from src.schemas.subject import subjectSchema
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify

subject_bp = Blueprint("subject", __name__)

@subject_bp.route("/api/create_subject", methods=["POST"])
def create_subj():
    try:
        data = subjectSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    name = data.get("name")
    teacher_id = data.get("teacher_id")
    course_code = data.get("course_code")

    result = create_subject(name, teacher_id, course_code)
    return result

@subject_bp.route("/api/get_subjects", methods=["GET"])
def get_subj():
    subject_id = request.args.get("id", type=int)

    if subject_id is None:
        return get_all_subjects()
        

    result = get_subject_by_id(subject_id)
    return result

@subject_bp.route("/api/delete_subject", methods=["DELETE"])
def delete_subj():
    subject_id = request.args.get("id", type=int)
    if not subject_id:
        return jsonify({
            "message": "Subject ID is required",
            "status": "error"
        }), 400
    result = delete_subject(subject_id)
    return result

@subject_bp.route("/api/update_subject", methods=["PUT"])
def update_subj():

    data = request.get_json()
    if not data:
        return jsonify({
            "message": "No data provided",
            "status": "error"
        }), 400
    
    subject_id = request.args.get("id", type=int)
    if not subject_id:
        return jsonify({
            "message": "Subject ID is required",
            "status": "error"
        }), 400
    result = update_subject(subject_id, **data)

    return result


    