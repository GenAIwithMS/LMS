from src.models.subject import Subject
from flask import jsonify
from src.db import db

def create_subject(name, teacher_id, course_code=None):
    new_subject = Subject(
        name=name,
        teacher_id=teacher_id,
        course_code=course_code
    )
    db.session.add(new_subject)
    db.session.commit()

    return jsonify({
        "message": "Subject created successfully",
        "status": "success"
    })

def get_all_subjects():
    subjects = Subject.query.all()
    subject_list = []
    for subject in subjects:
        subject_data = {
            "id": subject.id,
            "name": subject.name,
            "teacher_id": subject.teacher_id,
            "course_code": subject.course_code
        }
        subject_list.append(subject_data)
    
    return jsonify({
        "message": "Subjects retrieved successfully",
        "status": "success",
        "data": subject_list
    })

def get_subject_by_id(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "error"
        }), 400
    
    subject_data = {
        "id": subject.id,
        "name": subject.name,
        "teacher_id": subject.teacher_id,
        "course_code": subject.course_code
    }
    
    return jsonify({
        "message": "Subject retrieved successfully",
        "status": "success",
        "data": subject_data
    })

def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "error"
        }), 400
    
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({
        "message": "Subject deleted successfully",
        "status": "success"
    })

def update_subject(subject_id, **kwargs):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({
            "message": "Subject not found",
            "status": "error"
        }), 400
    
    for key, value in kwargs.items():
        if hasattr(subject, key):
            setattr(subject, key, value)
    
    db.session.commit()
    
    return jsonify({
        "message": "Subject updated successfully",
        "status": "success"
    })