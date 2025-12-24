from flask import Blueprint, request,jsonify
from src.db import db
from src.models.student import Student
from src.services.students import add_students, get_all_students, get_student_by_id, update_student, delete_student
from flask_jwt_extended import jwt_required , get_jwt
from src.schemas.auth_schema import RegisterStudentSchema
from marshmallow import ValidationError
# from src.services.user import add_user

student_bp = Blueprint("student",__name__)

@student_bp.route("/api/add_student",methods=["POST"])
def add_student():
    try:
        data = RegisterStudentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    if not data or not data.get('password'):
        return jsonify({"error": "Password is required"}), 400
    

    result = add_students(
        name=data['name'],
        username=data['username'],
        section=data['section_id'],
        password=data['password'],
        email=data.get('email'),
    )
    
    # add_user(
    #     email=data['email'],
    #     password=data['password'],
    #     user_role='student'
    #     )

    return result
   
@student_bp.route("/api/get_student", methods=["GET"])
@jwt_required()
def get_student():

    student_id = request.args.get("id", type=int)

    if student_id is None:
        if get_jwt()["role"] != "admin" and get_jwt()["role"] != "teacher":
            return jsonify({
                "message":"Only admin and teacher can access all student details"
            }),403
        return get_all_students()

    student_data = Student.query.get(student_id)

    if student_data is None:
        return jsonify({"error": "Student not found"}), 404
    
    result = get_student_by_id(student_id)
    return result 



@student_bp.route("/api/update_student",methods=["PUT"])
@jwt_required()
def update_student():
    
    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can update student details"
        }),403
    
    student_id = request.args.get("id",type=int)
    if student_id is None:
        return jsonify({"error":"invalid ID"}),400

    data = request.get_json()
    if not data:
        return jsonify({"error":"Missing json body"}),400
    
    result = update_student(student_id, **data)

    return result

@student_bp.route("/api/delete_student",methods=["DELETE"])
@jwt_required()
def delete_student():
    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can delete student"
        }),403
    
    student_id = request.args.get("id")
    if student_id is None:
        return jsonify({"error":"invalid ID"}),400
    
    result = delete_student(student_id)
    return result
    
