from src.schemas.attendance import AttendanceSchema, UpdateAttendanceSchema
from src.services.attendance import mark_attend, get_attendance_by_student,get_attendance_by_subject,get_all_attendance,update_attendance,delete_attendance
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required,get_jwt

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route("/api/attendance", methods=["POST"])
@jwt_required()
def create_attendance():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can create attendance",
            "status":"failed"
        }),403
    
    try:
        data = AttendanceSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    student_id = data['student_id']
    subject_id = data['subject_id']
    date = data['date']
    time = data['time']
    status = data['status']

    result = mark_attend(student_id, subject_id, date, time, status)
    return result

@attendance_bp.route("/api/get/attendance", methods=["GET"])
@jwt_required()
def fetch_attendance():
    student_id = request.args.get('student_id')
    subject_id = request.args.get('subject_id')

    if student_id:
        return get_attendance_by_student(student_id)
    elif subject_id:
        return get_attendance_by_subject(subject_id)
    else:
        return get_all_attendance()
    
@attendance_bp.route("/api/update/attendance", methods=["PUT"])
@jwt_required()
def modify_attendance():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can update attendance",
            "status":"failed"
        }),403
    
    attendance_id = request.args.get('attendance_id')
    if not attendance_id:
        return jsonify({
            "message": "attendance_id query parameter is required",
            "status": "error"
        }), 400

    try:
        data = UpdateAttendanceSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    result = update_attendance(attendance_id, data)
    return result

@attendance_bp.route("/api/delete/attendance", methods=["DELETE"])
@jwt_required()
def remove_attendance():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can delete attendance",
            "status":"failed"
        }),403
    
    attendance_id = request.args.get('attendance_id')
    if not attendance_id:
        return jsonify({
            "message": "attendance_id query parameter is required",
            "status": "error"
        }), 400

    result = delete_attendance(attendance_id)
    return result