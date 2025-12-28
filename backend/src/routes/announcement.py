from src.services.announsment import add_announcement,get_all_announcements,get_announcement_by_id,edit_announcement,delete_announcement
from flask import jsonify,request,Blueprint
from src.schemas.announcement import AnnouncementSchema,UpdateAnnouncementSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity
from src.models.section import Section

announcement_bp = Blueprint("announcement",__name__)

@announcement_bp.route("/api/create/announcement", methods=["POST"])
@jwt_required()
def create_announce():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can create announcement",
            "status":"failed"
        }),403
    
    
    try:
        data = AnnouncementSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    title = data.get("title")
    content = data.get("content")
    target_audience = data.get("target_audience", "all")
    section_name = data.get("section_name")
    teacher_id = int(get_jwt_identity())

    section = Section.query.filter_by(name=section_name).first()
    if not section:
        return jsonify({
            "message": "Section not found",
            "status": "failed"      
        }), 400

    result = add_announcement(
        title=title,
        content=content,
        target_audience=target_audience,
        section_id=section.id,
        teacher_id=teacher_id
    )
    return result

@announcement_bp.route("/api/get/announcements", methods=["GET"])
@jwt_required()
def fetch_all_announcements():
    announcement_id = request.args.get("id")
    if not announcement_id:
        result = get_all_announcements()
        return result

    result = get_announcement_by_id(announcement_id)
    return result

@announcement_bp.route("/api/update/announcement", methods=["PUT"])
@jwt_required()
def edit_announce():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can update announcement",
            "status":"failed"
        }),403
    
    try:
        data = UpdateAnnouncementSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    announcement_id = request.args.get("id")
    if not announcement_id:
        return jsonify({
            "message": "Announcement ID is required",
            "status": "error"
        }), 400

    if 'section_name' in data:
        section = Section.query.filter_by(name=data['section_name']).first()
        if not section:
            return jsonify({
                "message": "Section not found",
                "status": "failed"
            }), 400
        data['section_id'] = section.id
        del data['section_name']

    result = edit_announcement(announcement_id, **data)
    return result

@announcement_bp.route("/api/delete/announcement", methods=["DELETE"])
@jwt_required()
def delete_announce():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can delete announcement",
            "status":"failed"
        }),403
    
    announcement_id = request.args.get("id")
    if not announcement_id:
        return jsonify({
            "message": "Announcement ID is required",
            "status": "error"
        }), 400

    result = delete_announcement(announcement_id)
    return result