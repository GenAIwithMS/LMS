from src.models.course import Course
from flask import jsonify
from src.db import db


def add_course(name, description, course_code, teacher_id, created_at=None):
    new_course = Course(
        name=name,
        description=description,
        course_code=course_code,
        teacher_id=teacher_id
    )
    if created_at:
        new_course.created_at = created_at
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Course added successfully", "course_id": new_course.id}), 201

def get_all_courses():
    courses = Course.query.all()
    course_list = []
    for course in courses:
        course_data = {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "course_code": course.course_code,
            "teacher_id": course.teacher_id,
            "created_at": course.created_at
        }
        course_list.append(course_data)
    return jsonify(course_list)

def get_course_by_id(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 400
    course_data = {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "course_code": course.course_code,
        "teacher_id": course.teacher_id,
        "created_at": course.created_at
    }
    return jsonify(course_data)

def update_course(course_id, **kwargs):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 400
    for key, value in kwargs.items():
        if hasattr(course, key):
            setattr(course, key, value)
    db.session.commit()
    return jsonify({"message": "Course updated successfully"})

def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 400
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted successfully"})