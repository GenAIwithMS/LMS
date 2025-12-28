from src.services.assignment import add_assignment, get_assignment_by_id,get_all_assignments,edit_assignment,delete_assignment
from flask import Blueprint, request, jsonify
from src.schemas.assignment import assignmentSchema,UpdateAssignmentSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from src.models.subject import Subject

assignment_bp = Blueprint("assignment", __name__)

@assignment_bp.route("/api/create/assignments", methods=["POST"])
@jwt_required()
def create_assign():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can create assignment",
            "status":"failed"
        }),403
    
    try:
        data = assignmentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    subject_name = data.get("subject_name")
    teacher_id = int(get_jwt_identity())  
    total_marks = data.get("total_marks")

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "failed"
        }), 400

    result = add_assignment(title, description, teacher_id, due_date, subject.id, total_marks)
    return result

@assignment_bp.route("/api/get/assignments", methods=["GET"])
@jwt_required()
def get_assignments():
    assignment_id = request.args.get("id", type=int)
    if assignment_id:
        result = get_assignment_by_id(assignment_id)
    else:
        result = get_all_assignments()
    return result

@assignment_bp.route("/api/update/assignments/", methods=["PUT"])
@jwt_required()
def update_assignment():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can create assignment",
            "status":"failed"
        }),403
    
    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400
    try:
        data = UpdateAssignmentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    kwargs = {}
    for key, value in data.items():
        if key == 'subject_name':
            subject = Subject.query.filter_by(name=value).first()
            if not subject:
                return jsonify({"message": "Subject not found", "status": "failed"}), 400
            kwargs['subject_id'] = subject.id
        else:
            kwargs[key] = value

    result = edit_assignment(assignment_id, **kwargs)
    return result

@assignment_bp.route("/api/delete/assignments/", methods=["DELETE"])
@jwt_required()
def delete_assig():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can create assignment",
            "status":"failed"
        }),403
    
    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400

    result = delete_assignment(assignment_id)
    return result