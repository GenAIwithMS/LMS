from src.models.teacher import Teacher
from src.db import db
from flask import jsonify

def add_teacher(name,subject, username,email,password_hash):

    new_teacher = Teacher(
        name=name,
        subject=subject,
        username=username,
        email=email
    )
    new_teacher.set_password(password_hash)
    db.session.add(new_teacher)
    db.session.commit()
    
    return jsonify({
        "message":"teacher added sucessfully",
        "status":"sucess"
    })

def get_all_teachers():
    all_teachers = Teacher.query.all()

    teachers = []
    for teacher in all_teachers:
        teachers.append({
            "id": teacher.id,
            "name":teacher.name,
            "subject":teacher.subject,
            "username": teacher.username,
            "email": teacher.email
        })
    return jsonify(teachers)

def get_teacher_by_id(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({
            "message":"teacher not found",
            "status":"failed"
        }), 400
    teacher_data = {
        "id": teacher.id,
        "name": teacher.name,
        "username": teacher.username,
        "email": teacher.email,
        "subject": teacher.subject
    }
    return jsonify({
        "teacher": teacher_data
    })

def update_teacher(teacher_id, **kwargs):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({
            "message":"teacher not found",
            "status":"failed"
        }), 400
    
    for key, value in kwargs.items():
        if hasattr(teacher, key):
            setattr(teacher, key, value)
    
    db.session.commit()
    
    return jsonify({
        "message":"teacher updated successfully",
        "status":"success"
    })

def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({
            "message":"teacher not found",
            "status":"failed"
        }), 400
    
    db.session.delete(teacher)
    db.session.commit()
    
    return jsonify({
        "message":"teacher deleted successfully",
        "status":"success"
    })