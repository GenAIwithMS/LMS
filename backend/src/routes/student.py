from flask import Blueprint, request,jsonify
from src.db import db
from src.models.student import Student
from src.models.section import Section
from src.services.students import add_students, get_all_students, get_student_by_id, update_student, delete_student
from flask_jwt_extended import jwt_required , get_jwt, get_jwt_identity
from src.schemas.auth_schema import RegisterStudentSchema,UpdateStudentSchema
from marshmallow import ValidationError

student_bp = Blueprint("student",__name__)

@student_bp.route("/api/add/student",methods=["POST"])
@jwt_required()
def add_student():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can add student",
            "status":"failed"
        }),403
    
    try:
        data = RegisterStudentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    

    section_name = data['section_name']
    section = Section.query.filter_by(name=section_name).first()
    if not section:
        return jsonify({
            "message": "Section not found",
            "status": "failed"
        }), 400

    result = add_students(
        name=data['name'],
        username=data['username'],
        section=section.id,
        password=data['password'],
        email=data.get('email'),
    )
    

    return result
   
@student_bp.route("/api/get/student", methods=["GET"])
@jwt_required()
def get_student():

    student_id = request.args.get("id", type=int)
    token = get_jwt()
    user_role = token["role"]
    user_id = int(get_jwt_identity())

    if student_id is None:
        if user_role != "admin" and user_role != "teacher":
            return jsonify({
                "message":"Only admin and teacher can access all student details"
            }),403
        return get_all_students()

    student_data = Student.query.get(student_id)

    if student_data is None:
        return jsonify({"error": "Student not found"}), 404
    
    # Allow students to view their own data
    if user_role == "student" and student_id != user_id:
        return jsonify({
            "message":"You can only view your own student details"
        }),403
    
    result = get_student_by_id(student_id)
    return result 



@student_bp.route("/api/update/student",methods=["PUT"])
@jwt_required()
def update_std():
    
    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can update student details"
        }),403
    
    student_id = request.args.get("id",type=int)
    if student_id is None:
        return jsonify({"error":"invalid ID"}),400
    
    try:
        data = UpdateStudentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    kwargs = {}
    for key, value in data.items():
        if key == 'section_name':
            section = Section.query.filter_by(name=value).first()
            if not section:
                return jsonify({"message": "Section not found", "status": "failed"}), 400
            kwargs['section_id'] = section.id
        else:
            kwargs[key] = value

    result = update_student(student_id, **kwargs)

    return result

@student_bp.route("/api/delete/student",methods=["DELETE"])
@jwt_required()
def delete_std():

    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can delete student"
        }),403
    
    student_id = request.args.get("id", type=int)
    if student_id is None:
        return jsonify({"error":"invalid ID"}),400
    
    result = delete_student(student_id)
    return result
    
