from src.services import enroll_student,get_enrollments_by_course,get_enrollments_by_student,update_enrollment,delete_enrollment,get_all_enrollments
from src.schemas import EnrollmentSchema,UpdateEnrollmentSchema
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify,Blueprint,request
from marshmallow import ValidationError
from src.models import Student,Course

enrollment_bp = Blueprint("enrollment",__name__)

@enrollment_bp.route("/api/enroll/student", methods=["POST"])
@jwt_required()
def enroll_stu():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only adminn can enroll student",
            "status":"failed"
        }),403
    
    data = request.get_json()
    try:
        data = EnrollmentSchema().load(data)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    student_name = data.get("student_name")
    course_name = data.get("course_name")
    enrollment_date = data.get("enrollment_date")
    status = data.get("status", "active")
    grade = data.get("grade")

    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return jsonify({
            "message": "Student not found",
            "status": "failed"
        }), 400
    
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        return jsonify({
            "message": "Course not found",
            "status": "failed"
        }), 400

    result = enroll_student(
        student_id=student.id,
        course_id=course.id,
        enrollment_date=enrollment_date,
        status=status,
        grade=grade
    )
    return result

@enrollment_bp.route("/api/get/enrollments", methods=["GET"])
@jwt_required()
def get_enrollments():
    course_name = request.args.get("course_name")
    if course_name:
        course = Course.query.filter_by(name=course_name).first()
        if not course:
            return jsonify({"message": "Course not found", "status": "failed"}), 404
        result = get_enrollments_by_course(course.id)
        return result

    student_name = request.args.get("student_name")
    if student_name:
        student = Student.query.filter_by(name=student_name).first()
        if not student:
            return jsonify({"message": "Student not found", "status": "failed"}), 404
        result = get_enrollments_by_student(student.id)
        return result
    all_enrollments = get_all_enrollments()
    return all_enrollments

@enrollment_bp.route("/api/update/enrollment", methods=["PUT"])
@jwt_required()
def update_enroll():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admin can update enrollments",
            "status":"failed"
        }),403
    
    try:
        data = UpdateEnrollmentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    if not data:
        return jsonify({
            "message": "No data provided",
            "status": "error"
        }), 400
    
    enrollment_id = request.args.get("id", type=int)
    if not enrollment_id:
        return jsonify({
            "message": "Enrollment ID is required",
            "status": "error"
        }), 400

    kwargs = {}
    if 'student_name' in data:
        student = Student.query.filter_by(name=data['student_name']).first()
        if not student:
            return jsonify({"message": "Student not found", "status": "failed"}), 400
        kwargs['student_id'] = student.id
    if 'course_name' in data:
        course = Course.query.filter_by(name=data['course_name']).first()
        if not course:
            return jsonify({"message": "Course not found", "status": "failed"}), 400
        kwargs['course_id'] = course.id
    for key in ['enrollment_date', 'status', 'grade']:
        if key in data:
            kwargs[key] = data[key]

    result = update_enrollment(enrollment_id, **kwargs)
    if result is False:
        return jsonify({"message": "Enrollment not found", "status": "failed"}), 404
    return result

@enrollment_bp.route("/api/delete/enrollment", methods=["DELETE"])
@jwt_required()
def delete_enroll():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can delete",
            "status":"failed"
        }),403
    
    enrollment_id = request.args.get("id", type=int)
    if not enrollment_id:
        return jsonify({
            "message": "Enrollment ID is required",
            "status": "error"
        }), 400

    result = delete_enrollment(enrollment_id)
    return result