from src.models import Subject
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from src.db import db

def add_subject(name, teacher_id, course_id):
    new_subject = Subject(
        name=name,
        teacher_id=teacher_id,
        course_id=course_id
    )
    db.session.add(new_subject)
    db.session.commit()

    return jsonify({
        "message": "Subject created successfully",
        "status": "success"
    }), 201

def get_all_subjects():
    subjects = Subject.query.all()
    subject_list = []
    for subject in subjects:
        subject_data = {
            "id": subject.id,
            "name": subject.name,
            "teacher_id": subject.teacher_id,
            "teacher_name": subject.teacher.name if subject.teacher else None,
            "course_id": subject.course_id,
            "class_id": subject.class_id,
            "class_name": subject.school_class.name if subject.school_class else None,
            "course_name": subject.course.name if subject.course else None
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
        }), 404
    
    subject_data = {
        "id": subject.id,
        "name": subject.name,
        "teacher_id": subject.teacher_id,
        "teacher_name": subject.teacher.name if subject.teacher else None,
        "course_id": subject.course_id,
        "class_id": subject.class_id,
        "class_name": subject.school_class.name if subject.school_class else None,
        "course_name": subject.course.name if subject.course else None
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
        }), 404
    
    db.session.delete(subject)
    try:
        db.session.commit()
    except IntegrityError:
        # Other records still point to this one, so the database refuses
        db.session.rollback()
        return jsonify({
            "message": "Cannot delete this subject because it still has assignments, attendance or results. Delete those first.",
            "status": "failed"
        }), 409
    
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
        }), 404
    
    for key, value in kwargs.items():
        if hasattr(subject, key):
            setattr(subject, key, value)
    
    db.session.commit()
    
    return jsonify({
        "message": "Subject updated successfully",
        "status": "success"
    })
