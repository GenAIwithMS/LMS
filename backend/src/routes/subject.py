from src.services.subject import add_subject, get_all_subjects, get_subject_by_id, delete_subject,update_subject
from src.schemas.subject import subjectSchema,UpdateSubjectSchema
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from src.models.teacher import Teacher
from src.models.course import Course

subject_bp = Blueprint("subject", __name__)

@subject_bp.route("/api/create/subject", methods=["POST"])
@jwt_required()
def create_subj():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can create subject",
            "status":"failed"
        }),403
 
    try:
        data = subjectSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    teacher_name = data.get("teacher_name")
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return jsonify({
            "message": "Teacher not found",
            "status": "failed"
        }), 400
    
    course_name = data.get("course_name")
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        return jsonify({
            "message": "Course not found",
            "status": "failed"
        }), 400
    
    name = data.get("name")

    result = add_subject(name, teacher.id, course.id)
    return result

@subject_bp.route("/api/get/subjects", methods=["GET"])
@jwt_required()
def get_subj():
    subject_id = request.args.get("id", type=int)

    if subject_id is None:
        return get_all_subjects()
        

    result = get_subject_by_id(subject_id)
    return result

@subject_bp.route("/api/delete/subject", methods=["DELETE"])
@jwt_required()
def delete_subj():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can delete subject",
            "status":"failed"
        }),403
 
    subject_id = request.args.get("id", type=int)
    if not subject_id:
        return jsonify({
            "message": "Subject ID is required",
            "status": "error"
        }), 400
    result = delete_subject(subject_id)
    return result

@subject_bp.route("/api/update/subject", methods=["PUT"])
@jwt_required()
def update_subj():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can update subject",
            "status":"failed"
        }),403
 
    try:
        data = UpdateSubjectSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    subject_id = request.args.get("id", type=int)
    if not subject_id:
        return jsonify({
            "message": "Subject ID is required",
            "status": "error"
        }), 400

    kwargs = {}
    if 'name' in data:
        kwargs['name'] = data['name']
    if 'teacher_name' in data:
        teacher = Teacher.query.filter_by(name=data['teacher_name']).first()
        if not teacher:
            return jsonify({
                "message": "Teacher not found",
                "status": "failed"
            }), 400
        kwargs['teacher_id'] = teacher.id
    if 'course_name' in data:
        course = Course.query.filter_by(name=data['course_name']).first()
        if not course:
            return jsonify({
                "message": "Course not found",
                "status": "failed"
            }), 400
        kwargs['course_id'] = course.id

    result = update_subject(subject_id, **kwargs)

    return result


    