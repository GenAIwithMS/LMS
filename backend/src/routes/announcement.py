from src.services import add_announcement,get_all_announcements,get_announcement_by_title,edit_announcement,delete_announcement
from src.services.announsment import add_admin_announcement, edit_admin_announcement, delete_announcement_by_id
from flask import jsonify,request,Blueprint
from src.schemas import AnnouncementSchema,UpdateAnnouncementSchema, AdminAnnouncementSchema, UpdateAdminAnnouncementSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity
from src.models import Section, Announcement
from src.services.access import find_teacher_section, get_student_announcement_ids, get_teacher_announcement_ids, filter_response_by_ids, teacher_is_incharge


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

    section = find_teacher_section(teacher_id, section_name, data.get("section_id"))
    if not section:
        return jsonify({
            "message": "Section not found among your sections",
            "status": "failed"      
        }), 400

    # A class announcement: only for the section this teacher leads as class incharge
    as_incharge = data.get("as_incharge", False)
    if as_incharge and not teacher_is_incharge(teacher_id, section.id):
        return jsonify({
            "message": f"Only the class incharge of {section.full_name()} can post class announcements for it",
            "status": "failed"
        }), 403

    result = add_announcement(
        title=title,
        content=content,
        target_audience=target_audience,
        section_id=section.id,
        teacher_id=teacher_id,
        from_incharge=as_incharge
    )
    return result

@announcement_bp.route("/api/get/announcements", methods=["GET"])
@jwt_required()
def fetch_all_announcements():
    token = get_jwt()
    user_role = token["role"]

    announcement_title = request.args.get("title")
    if not announcement_title:
        # ?limit=5 gives only the newest few (the notification bell)
        limit = request.args.get("limit", type=int)
        if limit is not None and limit < 1:
            limit = None
        # Students and teachers only get the announcements meant for them (the admin sees all)
        allowed_ids = None
        if user_role == "student":
            allowed_ids = get_student_announcement_ids(int(get_jwt_identity()))
        if user_role == "teacher":
            allowed_ids = get_teacher_announcement_ids(int(get_jwt_identity()))
        return get_all_announcements(allowed_ids, limit)

    if user_role == "student" or user_role == "teacher":
        user_id = int(get_jwt_identity())
        allowed_ids = get_student_announcement_ids(user_id)
        if user_role == "teacher":
            allowed_ids = get_teacher_announcement_ids(user_id)
        announcement = Announcement.query.filter_by(title=announcement_title).first()
        if not announcement or announcement.id not in allowed_ids:
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

    if 'section_id' in data or 'section_name' in data:
        section = find_teacher_section(teacher_id, data.get('section_name'), data.get('section_id'))
        if not section:
            return jsonify({
                "message": "Section not found among your sections",
                "status": "failed"
            }), 400
        # A class announcement stays in a section this teacher leads
        announcement = Announcement.query.filter_by(title=announcement_title).first()
        if announcement.from_incharge and not teacher_is_incharge(teacher_id, section.id):
            return jsonify({
                "message": "A class announcement can only be for the section you lead as class incharge",
                "status": "failed"
            }), 403
        data['section_id'] = section.id
        data.pop('section_name', None)

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


# ---------------- Announcements from the admin

def only_admin():
    """An error answer if the user is not the admin, otherwise None."""
    if get_jwt().get("role") != "admin":
        return jsonify({"message": "Only the admin can do this", "status": "failed"}), 403
    return None


@announcement_bp.route("/api/admin/announcements", methods=["POST"])
@jwt_required()
def create_admin_announcement():
    error = only_admin()
    if error:
        return error
    try:
        data = AdminAnnouncementSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    admin_id = int(get_jwt_identity())
    return add_admin_announcement(admin_id, data["title"], data["content"], data["target_audience"],
                                  data.get("class_id"), data.get("section_id"))


@announcement_bp.route("/api/admin/announcements/<int:announcement_id>", methods=["PUT"])
@jwt_required()
def update_admin_announcement(announcement_id):
    error = only_admin()
    if error:
        return error
    try:
        data = UpdateAdminAnnouncementSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_admin_announcement(announcement_id, data)


@announcement_bp.route("/api/admin/announcements/<int:announcement_id>", methods=["DELETE"])
@jwt_required()
def remove_any_announcement(announcement_id):
    """The admin can delete any announcement, a teacher's too."""
    error = only_admin()
    if error:
        return error
    return delete_announcement_by_id(announcement_id)
