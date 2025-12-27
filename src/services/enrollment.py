from src.models.enrollment import Enrollment
from src.db import db
from flask import jsonify

def enroll_student(student_id, course_id, enrollment_date, status='active', grade=None):
    new_enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        enrollment_date=enrollment_date,
        status=status,
        grade=grade
    )
    db.session.add(new_enrollment)
    db.session.commit()
    return jsonify({"message": "Student enrolled successfully", "enrollment_id": new_enrollment.id}),201

def get_all_enrollments():
    enrollments = Enrollment.query.all()
    result = []
    for enrollment in enrollments:
        enrollment_data = {
            "id": enrollment.id,
            "student_name": enrollment.student.name,
            "course_name": enrollment.course.name,
            "enrollment_date": enrollment.enrollment_date,
            "status": enrollment.status,
            "grade": enrollment.grade
        }
        result.append(enrollment_data)
    return jsonify(result)

def get_enrollments_by_student(student_id):
    enrollments = Enrollment.query.filter_by(student_id=student_id)
    result = []
    for enrollment in enrollments:
        enrollment_data = {
            "id": enrollment.id,
            "course_name": enrollment.course.name,
            "enrollment_date": enrollment.enrollment_date,
            "status": enrollment.status,
            "grade": enrollment.grade
        }
        result.append(enrollment_data)

    return jsonify(result)

def get_enrollments_by_course(course_id):
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    result = []
    for enrollment in enrollments:
        enrollment_data = {
            "id": enrollment.id,
            "student_name": enrollment.student.name,
            "enrollment_date": enrollment.enrollment_date,
            "status": enrollment.status,
            "grade": enrollment.grade
        }
        result.append(enrollment_data)
    return jsonify(result)

def update_enrollment(enrollment_id, **kwargs):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return None
    for key, value in kwargs.items():
        if hasattr(enrollment, key):
            setattr(enrollment, key, value)
    db.session.commit()
    return jsonify({"message": "Enrollment updated successfully"}), 200

def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return False
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrollment deleted successfully"}), 200