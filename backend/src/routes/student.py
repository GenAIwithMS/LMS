from src.services.delete_checks import get_student_delete_check
from flask import Blueprint, request,jsonify
from src.models import Section,Student
from src.services import add_students, get_all_students, get_student_by_id, update_student, delete_student
from flask_jwt_extended import jwt_required , get_jwt, get_jwt_identity
from src.schemas import RegisterStudentSchema,UpdateStudentSchema
from marshmallow import ValidationError
from src.services.access import get_teacher_student_ids, filter_response_by_ids
from src.services.access import find_record

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
    

    section = find_record(Section, data.get('section_id'), data.get('section_name'))
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
        roll_number=data.get('roll_number'),
        admission_number=data.get('admission_number'),
        guardian_name=data.get('guardian_name'),
        guardian_phone=data.get('guardian_phone'),
        date_of_birth=data.get('date_of_birth'),
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
        result = get_all_students()
        # A teacher only sees their own students
        if user_role == "teacher":
            result = filter_response_by_ids(result, get_teacher_student_ids(user_id))
        return result

    student_data = Student.query.get(student_id)

    if student_data is None:
        return jsonify({"error": "Student not found"}), 404
    
    # Allow students to view their own data
    if user_role == "student" and student_id != user_id:
        return jsonify({
            "message":"You can only view your own student details"
        }),403

    if user_role == "teacher" and student_id not in get_teacher_student_ids(user_id):
        return jsonify({
            "message":"You can only view your own students"
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
        if key == 'section_id' or key == 'section_name':
            # The ID wins when both are sent
            if key == 'section_name' and 'section_id' in data:
                continue
            section = find_record(Section, data.get('section_id'), data.get('section_name'))
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
    
    # The admin has seen the student's records and chose to delete them too
    remove_records = request.args.get("remove_records", "false").lower() == "true"
    result = delete_student(student_id, remove_records)
    return result
    


@student_bp.route("/api/admin/students/<int:student_id>/delete-check", methods=["GET"])
@jwt_required()
def student_delete_check(student_id):
    """What the student still has, shown before deleting them."""
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Only the admin can delete students", "status": "failed"}), 403
    return get_student_delete_check(student_id)
