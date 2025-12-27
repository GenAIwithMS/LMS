from src.services.course import add_course,get_all_courses,get_course_by_id,update_course,delete_course
from src.schemas.course import CourseSchema, UpdateCourseSchema
from flask import jsonify,Blueprint,request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt
from src.models.teacher import Teacher

course_bp = Blueprint("course",__name__)

@course_bp.route("/api/add/course",methods=["POST"])
@jwt_required()
def add_cour():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can add courses",
            "status":"failed"
        }),403
    
    try:
        data = CourseSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    name = data.get("name")
    description = data.get("description")
    course_code = data.get("course_code")
    teacher_name = data.get("teacher_name")
    created_at = data.get("created_at")

    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return jsonify({
            "message": "Teacher not found",
            "status": "failed"
        }), 400

    result = add_course(
        name=name,
        description=description,
        course_code=course_code,
        created_at=created_at,
        teacher_id=teacher.id
    )
    return result

@course_bp.route("/api/get/courses", methods=["GET"])
@jwt_required()
def get_cour():
    course_id = request.args.get("id", type=int)

    if course_id is None:
        return get_all_courses()
        

    result = get_course_by_id(course_id)
    return result

@course_bp.route("/api/update/course", methods=["PUT"])
@jwt_required()
def update_cour():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can update course",
            "status":"failed"
        }),403
    
    try:
        data = UpdateCourseSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    course_id = request.args.get("id", type=int)
    if not course_id:
        return jsonify({
            "message": "Course ID is required",
            "status": "error"
        }), 400

    if 'teacher_name' in data:
        teacher = Teacher.query.filter_by(name=data['teacher_name']).first()
        if not teacher:
            return jsonify({
                "message": "Teacher not found",
                "status": "failed"
            }), 400
        data['teacher_id'] = teacher.id
        del data['teacher_name']

    result = update_course(course_id, **data)
    return result

@course_bp.route("/api/delete/course", methods=["DELETE"])
@jwt_required()
def delete_cour():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can delete course",
            "status":"failed"
        }),403
    
    course_id = request.args.get("id", type=int)
    if not course_id:
        return jsonify({
            "message": "Course ID is required",
            "status": "error"
        }), 400
    result = delete_course(course_id)
    return result




