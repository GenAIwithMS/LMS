from src.schemas.attendance import AttendanceSchema, UpdateAttendanceSchema
from src.services.attendance import mark_attend, get_attendance_by_student,get_attendance_by_subject,get_all_attendance,update_attendance,delete_attendance
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required,get_jwt
from src.models.student import Student
from src.models.subject import Subject
from src.models.attendance import Attendance

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
    
    student_name = data['student_name']
    subject_name = data['subject_name']
    status = data['status']

    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return jsonify({
            "message": "Student not found",
            "status": "failed"
        }), 400

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "failed"
        }), 400

    result = mark_attend(student.id, subject.id,status)
    return result

@attendance_bp.route("/api/get/attendance", methods=["GET"])
@jwt_required()
def fetch_attendance():
    student_name = request.args.get('student_name')
    subject_name = request.args.get('subject_name')

    if student_name:
        student = Student.query.filter_by(name=student_name).first()
        if not student:
            return jsonify({
                "message": "Student not found",
                "status": "failed"
            }), 400
        return get_attendance_by_student(student.id)
    elif subject_name:
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            return jsonify({
                "message": "Subject not found",
                "status": "failed"
            }), 400
        return get_attendance_by_subject(subject.id)
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
    
    attendance_id = request.args.get('id')
    if not attendance_id:
        return jsonify({
            "message": "attendance_id query parameter is required",
            "status": "error"
        }), 400

    try:
        data = UpdateAttendanceSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    if 'student_name' in data:
        student = Student.query.filter_by(name=data['student_name']).first()
        if not student:
            return jsonify({
                "message": "Student not found",
                "status": "failed"
            }), 400
        data['student_id'] = student.id
        del data['student_name']

    if 'subject_name' in data:
        subject = Subject.query.filter_by(name=data['subject_name']).first()
        if not subject:
            return jsonify({
                "message": "Subject not found",
                "status": "failed"
            }), 400
        data['subject_id'] = subject.id
        del data['subject_name']

    result = update_attendance(attendance_id, **data)
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
    
    data = request.get_json()
    student_name = data.get('student_name')
    subject_name = data.get('subject_name')
    
    if not student_name or not subject_name:
        return jsonify({
            "message": "student_name and subject_name are required in the request body",
            "status": "error"
        }), 400

    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return jsonify({
            "message": "Student not found",
            "status": "failed"
        }), 400

    subject = Subject.query.filter_by(name=subject_name).first()
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "failed"
        }), 400

    attendance_record = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id).order_by(Attendance.mark_at.desc()).first()
    if not attendance_record:
        return jsonify({
            "message": "Attendance record not found for this student and subject",
            "status": "failed"
        }), 404

    result = delete_attendance(attendance_record.id)
    return result