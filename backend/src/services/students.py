from src.models import Student,Enrollment
from src.services.users import is_email_taken, is_username_taken
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from src.db import db



def add_students(name, username, section, password, email):
    if is_email_taken(email):
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    if is_username_taken(username):
        return jsonify({
            "message":"Username already exists",
            "status":"failed"
        }), 400
    
    new_student = Student(
        name=name,
        username=username,
        section_id=section,
        email=email,
    )


    new_student.set_password(password)
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({
        "message":"student added successfully",
        "status":"success"
    }), 201

def get_all_students():
    students = Student.query.all()
    if not students:
        return jsonify({
            "message":"no students found",
            "status":"failed"
        }), 404
    
    student_list = []
    for student in students:
        student_data = {
            "id": student.id,
            "name": student.name,
            "username": student.username,
            "section_name": student.section.name,
            "email": student.email,
        }
        student_list.append(student_data)
    return jsonify(student_list)

def get_student_by_id(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({
            "message":"student not found",
            "status":"failed"
        }), 404
    
    student_data = {
        "id": student.id,
        "name": student.name,
        "username": student.username,
        "section_name": student.section.name,
        "email": student.email,
    }
    return jsonify({
        "student": student_data
    })


def update_student(student_id, **kwargs):

    student = Student.query.get(student_id)

    if not student:
        return jsonify({
            "message":"student not found",
            "status":"failed"
        }), 400
    
    if "email" in kwargs and is_email_taken(kwargs["email"], current_user=student):
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    if "username" in kwargs and is_username_taken(kwargs["username"], current_user=student):
        return jsonify({
            "message":"Username already exists",
            "status":"failed"
        }), 400

    for key, value in kwargs.items():
        if value is None:
            continue
        if key == 'password':
            student.set_password(value)
        elif hasattr(student, key):
            setattr(student, key, value)

    db.session.commit()
    
    return jsonify({
        "message":"student updated successfully",
        "status":"success"
    })

def delete_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({
            "message":"student not found",
            "status":"failed"
        }), 404

    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)

    db.session.delete(student)
    try:
        db.session.commit()
    except IntegrityError:
        # Other records still point to this one, so the database refuses
        db.session.rollback()
        return jsonify({
            "message": "Cannot delete this student because attendance, results or submissions still belong to them. Delete those first.",
            "status": "failed"
        }), 409

    return jsonify({
        "message":"student deleted successfully",
        "status":"success"
    })