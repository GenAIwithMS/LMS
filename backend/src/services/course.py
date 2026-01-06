from src.models import Course,Enrollment,Subject,Assignment,AssignmentSubmission,Result,Attendance,Teacher
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
        teacher = Teacher.query.get(course.teacher_id)
        course_data = {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "course_code": course.course_code,
            "teacher_name": teacher.name if teacher else None,
            "created_at": course.created_at
        }
        course_list.append(course_data)
    return jsonify(course_list)

def get_course_by_id(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404
    teacher = Teacher.query.get(course.teacher_id)
    course_data = {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "course_code": course.course_code,
        "teacher_name": teacher.name if teacher else None,
        "created_at": course.created_at
    }
    return jsonify(course_data)

def update_course(course_id, **kwargs):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404
    for key, value in kwargs.items():
        if hasattr(course, key):
            setattr(course, key, value)
    db.session.commit()
    return jsonify({"message": "Course updated successfully"})

def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404
    
    subjects = Subject.query.filter_by(course_id=course_id).all()
    subject_ids = [s.id for s in subjects]
    
    for subject_id in subject_ids:
        assignments = Assignment.query.filter_by(subject_id=subject_id).all()
        assignment_ids = [a.id for a in assignments]
        AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id.in_(assignment_ids)).delete()
    
    Assignment.query.filter(Assignment.subject_id.in_(subject_ids)).delete()
    
    Result.query.filter(Result.subject_id.in_(subject_ids)).delete()
    
    Attendance.query.filter(Attendance.subject_id.in_(subject_ids)).delete()
    
    Subject.query.filter_by(course_id=course_id).delete()
    
    Enrollment.query.filter_by(course_id=course_id).delete()
    
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted successfully"})