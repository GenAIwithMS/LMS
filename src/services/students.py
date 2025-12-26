from src.models.student import Student
from src.models.teacher import Teacher
from flask import jsonify
from src.db import db



def add_students(name, username, section, password, email, teacher_id):
        #check email or username already exists
    existing_email = Student.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    existing_username = Student.query.filter_by(username=username).first()
    if existing_username:
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

    teacher = Teacher.query.get(teacher_id)
    new_student.teachers.append(teacher)
    new_student.set_password(password)
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({
        "message":"student added sucessfully",
        "status":"sucess"
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
            "section": student.section,
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
        "section": student.section,
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
    
    for key, value in kwargs.items():
        if value is not None and hasattr(student, key):
            setattr(student, key, value)

    db.session.commit()
    
    return jsonify({
        "message":"student updated sucessfully",
        "status":"sucess"
    })

def delete_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({
            "message":"student not found",
            "status":"failed"
        }), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({
        "message":"student deleted sucessfully",
        "status":"sucess"
    })