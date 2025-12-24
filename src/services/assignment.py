from src.models.assignment import Assignment
from flask import jsonify
from src.db import db

def create_assignment(title, description,student_id, due_date,subject_id, total_marks):
    new_assignment = Assignment(
        title=title,
        description=description,
        due_date=due_date,
        subject_id=subject_id,
        total_marks=total_marks,
        student_id=student_id
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({
        "message": "Assignment created successfully",
        "status": "success"
    })

def get_assignment_by_id(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({
            "message": "Assignment not found",
            "status": "error"
        }),400

    return jsonify({
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date,
            "subject_id": assignment.subject_id,
            "student_id": assignment.student_id,
            "total_marks": str(assignment.total_marks)
        },
        "status": "success"
    })

def get_all_assignments():
    assignments = Assignment.query.all()
    result = []
    for assignment in assignments:
        result.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date,
            "subject_id": assignment.subject_id,
            "student_id": assignment.student_id,
            "total_marks": str(assignment.total_marks)
        })

    return jsonify({
        "assignments": result,
        "status": "success"
    })

def edit_assignment(assignment_id, **kwargs):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({
            "message": "Assignment not found",
            "status": "error"
        }),400

    for key, value in kwargs.items():
        if value is not None and hasattr(assignment, key):
            setattr(assignment, key, value)

    db.session.commit()

    return jsonify({
        "message": "Assignment updated successfully",
        "status": "success"
    })

def delete_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({
            "message": "Assignment not found",
            "status": "error"
        }),400

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({
        "message": "Assignment deleted successfully",
        "status": "success"
    })