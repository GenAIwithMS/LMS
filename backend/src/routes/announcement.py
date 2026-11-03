from src.services import add_announcement,get_all_announcements,get_announcement_by_title,edit_announcement,delete_announcement
from flask import jsonify,request,Blueprint
from src.schemas import AnnouncementSchema,UpdateAnnouncementSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity
from src.models import Section, Announcement
from src.services.access import find_teacher_section, get_student_announcement_ids, filter_response_by_ids


def teacher_owns_announcement(teacher_id, announcement_title):
    """True if this teacher posted the announcement with this title."""
    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement:
        return False
    return announcement.teacher_id == teacher_id

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

    section = find_teacher_section(teacher_id, section_name)
    if not section:
        return jsonify({
            "message": "Section not found among your sections",
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
    token = get_jwt()
    user_role = token["role"]

    announcement_title = request.args.get("title")
    if not announcement_title:
        result = get_all_announcements()
        # A student only sees announcements for their section, plus school-wide ones
        if user_role == "student":
            student_id = int(get_jwt_identity())
            result = filter_response_by_ids(result, get_student_announcement_ids(student_id))
        return result

    if user_role == "student":
        student_id = int(get_jwt_identity())
        announcement = Announcement.query.filter_by(title=announcement_title).first()
        if not announcement or announcement.id not in get_student_announcement_ids(student_id):
            return jsonify({
                "message": "Announcement not found",
                "status": "failed"
            }), 404

    result = get_announcement_by_title(announcement_title)
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
    
    announcement_title = request.args.get("title")
    if not announcement_title:
        return jsonify({
            "message": "Announcement title is required",
            "status": "error"
        }), 400

    teacher_id = int(get_jwt_identity())
    if not teacher_owns_announcement(teacher_id, announcement_title):
        return jsonify({
            "message": "You can only update your own announcements",
            "status": "failed"
        }), 403

    if 'section_name' in data:
        section = find_teacher_section(teacher_id, data['section_name'])
        if not section:
            return jsonify({
                "message": "Section not found among your sections",
                "status": "failed"
            }), 400
        data['section_id'] = section.id
        del data['section_name']

    result = edit_announcement(announcement_title, **data)
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
    
    announcement_title = request.args.get("title")
    if not announcement_title:
        return jsonify({
            "message": "Announcement title is required",
            "status": "error"
        }), 400

    teacher_id = int(get_jwt_identity())
    if not teacher_owns_announcement(teacher_id, announcement_title):
        return jsonify({
            "message": "You can only delete your own announcements",
            "status": "failed"
        }), 403

    result = delete_announcement(announcement_title)
    return result