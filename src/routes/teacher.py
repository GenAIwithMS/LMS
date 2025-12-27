from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required,get_jwt
from src.schemas.auth_schema import RegisterTeacherSchema,UpdateTeacherSchema
from marshmallow import ValidationError
from src.services.teacher import add_teacher, get_teacher_by_id, update_teacher, delete_teacher, get_all_teachers

teacher_bp = Blueprint("teacher",__name__)

@teacher_bp.route("/api/add/teacher", methods=["POST"])
@jwt_required()
def add_teach():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can add teacher"
        }),403
    
    try:
        data_of_teacher = RegisterTeacherSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    result = add_teacher(
        name=data_of_teacher["name"],
        username=data_of_teacher["username"],
        email=data_of_teacher.get("email"),
        password_hash=data_of_teacher["password_hash"]
    )
    return result


@teacher_bp.route("/api/get/teacher")
@jwt_required()
def get_teacher():
    
    
    teacher_id = request.args.get("id",type=int)

    if teacher_id is None:
        if get_jwt()["role"] != "admin":
            return jsonify({
                "message":"Admins have acess to see all the teacher's!"
            }),403
        
        result = get_all_teachers()
        return result
        
    result = get_teacher_by_id(teacher_id)

    return result
    

@teacher_bp.route("/api/update/teacher",methods=["PUT"])
@jwt_required()
def update_techer():
    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can update teacher details"
        }),403
    
    teacher_id = request.args.get("id",type=int)

    if teacher_id is None:
        return jsonify({
            "error":"Invalid ID"
        }),400
    
    try:
        teacher_data = UpdateTeacherSchema().load(request.get_json(silent=True))
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    result = update_teacher(teacher_id, **teacher_data)
    return result


@teacher_bp.route("/api/delete/teacher",methods=["DELETE"])
@jwt_required()
def del_teacher():
    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can delete teacher"
        }),403

    teacehr_id = request.args.get("id",type=int)
    if not teacehr_id:
        return jsonify({
            "eror":"messsage"
        }),400
    result = delete_teacher(teacehr_id)
    return result



