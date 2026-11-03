from src.schemas import AttendanceSchema, UpdateAttendanceSchema
from src.services import mark_attend, get_attendance_by_student,get_attendance_by_subject,get_all_attendance,update_attendance,delete_attendance
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required,get_jwt,get_jwt_identity
from src.models import Student,Attendance,Subject
from src.services.access import find_teacher_student, find_teacher_subject, get_teacher_subject_ids, filter_response_by_ids


def teacher_can_access_attendance(teacher_id, attendance_id):
    """True if the attendance record is in a subject this teacher teaches."""
    record = Attendance.query.get(attendance_id)
    if not record:
        return False
    return record.subject_id in get_teacher_subject_ids(teacher_id)


def get_teacher_attendance_ids(teacher_id):
    """IDs of all attendance records in the subjects this teacher teaches."""
    attendance_ids = []
    for subject_id in get_teacher_subject_ids(teacher_id):
        records = Attendance.query.filter_by(subject_id=subject_id).all()
        for record in records:
            attendance_ids.append(record.id)
    return attendance_ids

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
    teacher_id = int(get_jwt_identity())

    student = find_teacher_student(teacher_id, student_name)
    if not student:
        return jsonify({
            "message": "Student not found among your students",
            "status": "failed"
        }), 400

    subject = find_teacher_subject(teacher_id, subject_name)
    if not subject:
        return jsonify({
            "message": "Subject not found among the subjects you teach",
            "status": "failed"
        }), 400

    result = mark_attend(student.id, subject.id,status)
    return result

@attendance_bp.route("/api/get/attendance", methods=["GET"])
@jwt_required()
def fetch_attendance():
    # Students only ever get their own records, whatever filters they send.
    if get_jwt().get("role") == "student":
        own_records = Attendance.query.filter_by(student_id=int(get_jwt_identity())).all()
        if not own_records:
            return jsonify([]), 200
        return get_attendance_by_student(int(get_jwt_identity()))

    student_name = request.args.get('student_name')
    subject_name = request.args.get('subject_name')

    if student_name:
        student = Student.query.filter_by(name=student_name).first()
        if not student:
            return jsonify({
                "message": "Student not found",
                "status": "failed"
            }), 400
        result = get_attendance_by_student(student.id)
    elif subject_name:
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            return jsonify({
                "message": "Subject not found",
                "status": "failed"
            }), 400
        result = get_attendance_by_subject(subject.id)
    else:
        result = get_all_attendance()

    # A teacher only sees attendance in the subjects they teach
    if get_jwt().get("role") == "teacher":
        teacher_id = int(get_jwt_identity())
        result = filter_response_by_ids(result, get_teacher_attendance_ids(teacher_id))

    return result
    
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

    teacher_id = int(get_jwt_identity())
    if not teacher_can_access_attendance(teacher_id, int(attendance_id)):
        return jsonify({
            "message": "You can only update attendance in subjects you teach",
            "status": "failed"
        }), 403

    try:
        data = UpdateAttendanceSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    if 'student_name' in data:
        student = find_teacher_student(teacher_id, data['student_name'])
        if not student:
            return jsonify({
                "message": "Student not found among your students",
                "status": "failed"
            }), 400
        data['student_id'] = student.id
        del data['student_name']

    if 'subject_name' in data:
        subject = find_teacher_subject(teacher_id, data['subject_name'])
        if not subject:
            return jsonify({
                "message": "Subject not found among the subjects you teach",
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
    
    teacher_id = int(get_jwt_identity())

    attendance_id = request.args.get('id', type=int)
    if attendance_id:
        if not teacher_can_access_attendance(teacher_id, attendance_id):
            return jsonify({
                "message": "You can only delete attendance in subjects you teach",
                "status": "failed"
            }), 403
        result = delete_attendance(attendance_id)
        return result
    
    student_name = request.args.get('student_name')
    subject_name = request.args.get('subject_name')
    
    if not student_name or not subject_name:
        return jsonify({
            "message": "Either attendance_id or both student_name and subject_name are required as query parameters",
            "status": "error"
        }), 400

    student = find_teacher_student(teacher_id, student_name)
    if not student:
        return jsonify({
            "message": "Student not found among your students",
            "status": "failed"
        }), 400

    subject = find_teacher_subject(teacher_id, subject_name)
    if not subject:
        return jsonify({
            "message": "Subject not found among the subjects you teach",
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