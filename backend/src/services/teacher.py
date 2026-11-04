from src.models import TeacherSubject
from src.models import Teacher
from src.services.users import is_email_taken, is_username_taken
from src.db import db
from flask import jsonify
from sqlalchemy.exc import IntegrityError

def add_teacher(name, username, email, password_hash):
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
    
    new_teacher = Teacher(
        name=name,
        username=username,
        email=email
    )

    new_teacher.set_password(password_hash)
    db.session.add(new_teacher)
    db.session.commit()
    
    return jsonify({
        "message":"teacher added successfully",
        "status":"success"
    }), 201

def get_all_teachers():
    all_teachers = Teacher.query.all()

    teachers = []
    for teacher in all_teachers:
        teachers.append({
            "id": teacher.id,
            "name":teacher.name,
            "subjects": [subject.name for subject in teacher.subjects],
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
        }), 404
    teacher_data = {
        "id": teacher.id,
        "name": teacher.name,
        "username": teacher.username,
        "email": teacher.email,
        "subjects": [subject.name for subject in teacher.subjects]
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
        }), 404
    
    if "email" in kwargs and is_email_taken(kwargs["email"], current_user=teacher):
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    if "username" in kwargs and is_username_taken(kwargs["username"], current_user=teacher):
        return jsonify({
            "message":"Username already exists",
            "status":"failed"
        }), 400

    for key, value in kwargs.items():
        if key == 'password':
            teacher.set_password(value)
        elif hasattr(teacher, key):
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
    
    # The list of subjects they can teach goes with them
    TeacherSubject.query.filter_by(teacher_id=teacher_id).delete()
    db.session.delete(teacher)
    try:
        db.session.commit()
    except IntegrityError:
        # Other records still point to this one, so the database refuses
        db.session.rollback()
        return jsonify({
            "message": "Cannot delete this teacher because they still have courses, subjects, sections, assignments or announcements. Reassign or delete those first.",
            "status": "failed"
        }), 409
    
    return jsonify({
        "message":"teacher deleted successfully",
        "status":"success"
    })