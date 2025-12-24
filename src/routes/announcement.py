from src.services.announsment import create_announcement,get_all_announcements,get_announcement_by_id,edit_announcement,delete_announcement
from flask import jsonify,request,Blueprint
from src.schemas.announcement import AnnouncementSchema
from marshmallow import ValidationError

announcement_bp = Blueprint("announcement",__name__)

@announcement_bp.route("/api/create-announcement", methods=["POST"])
def create_announce():
    try:
        data = AnnouncementSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    title = data.get("title")
    content = data.get("content")
    target_audience = data.get("target_audience", "all")
    section_id = data.get("section_id")
    teacher_id = data.get("teacher_id")

    result = create_announcement(
        title=title,
        content=content,
        target_audience=target_audience,
        section_id=section_id,
        teacher_id=teacher_id
    )
    return result

@announcement_bp.route("/api/get/announcements", methods=["GET"])
def fetch_all_announcements():
    announcement_id = request.args.get("announcement_id")
    if not announcement_id:
        result = get_all_announcements()
        return result

    result = get_announcement_by_id(announcement_id)
    return result

@announcement_bp.route("/api/update/announcement", methods=["PUT"])
def edit_announce():
    data = request.get_json()
    announcement_id = request.args.get("id")
    if not announcement_id:
        return jsonify({
            "message": "Announcement ID is required",
            "status": "error"
        }), 400

    result = edit_announcement(announcement_id, **data)
    return result

@announcement_bp.route("/api/delete/announcement", methods=["DELETE"])
def delete_announce():
    announcement_id = request.args.get("announcement_id")
    if not announcement_id:
        return jsonify({
            "message": "Announcement ID is required",
            "status": "error"
        }), 400

    result = delete_announcement(announcement_id)
    return result