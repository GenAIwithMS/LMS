from src.services.section import add_section,get_all_sections,get_section_by_id,edit_section,delete_section
from flask import Blueprint, request, jsonify
from src.schemas.section import SectionSchema,UpdateSectionSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required,get_jwt

section_bp = Blueprint("section", __name__)

@section_bp.route("/api/add_section", methods=["POST"])
@jwt_required()
def add_sec():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admin can add section",
            "status":"failed"
        }),403

    try:
        data = SectionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    name = data.get("name")
    teacher_id = data.get("teacher_id")
    
    result = add_section(name, teacher_id)
    return result

@section_bp.route("/api/get_section", methods=["GET"])
@jwt_required()
def get_sec():
    section_id = request.args.get("id", type=int)
    if section_id is None:
        result = get_all_sections()
        return result

    result = get_section_by_id(section_id)
    return result

@section_bp.route("/api/update/section", methods=["PUT"])
@jwt_required()
def update_sec():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admin can update section",
            "status":"failed"
        }),403

    section_id = request.args.get("id", type=int)
    if not section_id:
        return jsonify({
            "message": "Section ID is required",
            "status": "error"
        }), 400
    try:
        data = UpdateSectionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    result = edit_section(section_id, **data)
    return result

@section_bp.route("/api/delete/section", methods=["DELETE"])
@jwt_required()
def delete_sec():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admin can delete section"
        })

    section_id = request.args.get("id", type=int)
    if not section_id:
        return jsonify({
            "message": "Section ID is required",
            "status": "error"
        }), 400

    result = delete_section(section_id)
    return result