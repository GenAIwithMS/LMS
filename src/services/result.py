from src.models.result import Result
from flask import jsonify
from src.db import db

def calculate_grade(obtained_marks, total_marks):
    if total_marks is None or obtained_marks is None:
        return jsonify({
            "message": "Marks cannot be None",
            "status": "error"
        }), 400
    if total_marks <= 0:
        return jsonify({
            "message": "Total marks must be greater than zero",
            "status": "error"
        }), 400
    
    percentage = (obtained_marks / total_marks) * 100
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'
    
def add_result(subject_id, student_id, total_marks,obtained_marks, exam_type, remarks=None):
    new_result = Result(
        subject_id=subject_id,
        student_id=student_id,
        total_marks=total_marks,
        obtained_marks=obtained_marks,
        exam_type=exam_type,
        remarks=remarks
    )
    grade = calculate_grade(obtained_marks, total_marks)
    new_result.grade = grade
    db.session.add(new_result)
    db.session.commit()

    return jsonify({
        "message": "Result added successfully",
        "status": "success"
    }), 201

def get_result_by_id(result_id):
    result = Result.query.get(result_id)
    if not result:
        return jsonify({
            "message": "Result not found",
            "status": "error"
        }), 404

    return jsonify({
        "id": result.id,
        "subject_name": result.subject.name,
        "student_name": result.student.name,
        "total_marks": float(result.total_marks),
        "obtained_marks": float(result.obtained_marks),
        "grade": result.grade,
        "exam_type": result.exam_type,
        "remarks": result.remarks
    })

def get_all_results():
    results = Result.query.all()
    results_list = []
    for result in results:
        results_list.append({
            "id": result.id,
            "subject_name": result.subject.name,
            "student_name": result.student.name,
            "total_marks": float(result.total_marks),
            "obtained_marks": float(result.obtained_marks),
            "grade": result.grade,
            "exam_type": result.exam_type,
            "remarks": result.remarks
        })
    return jsonify(results_list)

def edit_result(result_id, **kwargs):
    result = Result.query.get(result_id)
    if not result:
        return jsonify({
            "message": "Result not found",
            "status": "error"
        }), 404

    for key, value in kwargs.items():
        if hasattr(result, key):
            setattr(result, key, value)

    if 'obtained_marks' in kwargs or 'total_marks' in kwargs:
        obtained_marks = kwargs.get('obtained_marks', result.obtained_marks)
        total_marks = kwargs.get('total_marks', result.total_marks)
        result.grade = calculate_grade(obtained_marks, total_marks)

    db.session.commit()

    return jsonify({
        "message": "Result updated successfully",
        "status": "success"
    })

def delete_result(result_id):
    result = Result.query.get(result_id)
    if not result:
        return jsonify({
            "message": "Result not found",
            "status": "error"
        }), 404

    db.session.delete(result)
    db.session.commit()

    return jsonify({
        "message": "Result deleted successfully",
        "status": "success"
    })