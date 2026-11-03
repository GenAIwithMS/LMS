from src.models import Result
from flask import jsonify
from src.db import db

EXAM_TYPES = ['midterm', 'final', 'quiz', 'assignment']


def check_result_values(obtained_marks, total_marks, exam_type=None):
    """Return an error message if the values can't be saved, otherwise None."""
    if total_marks is None or obtained_marks is None:
        return "Total marks and obtained marks are both required"

    try:
        total = float(total_marks)
        obtained = float(obtained_marks)
    except (TypeError, ValueError):
        return "Marks must be numbers"

    if total <= 0:
        return "Total marks must be greater than zero"
    if obtained < 0:
        return "Obtained marks cannot be negative"
    if obtained > total:
        return "Obtained marks cannot be more than total marks"

    if exam_type is not None and exam_type not in EXAM_TYPES:
        return "Exam type must be one of: " + ", ".join(EXAM_TYPES)

    return None


def calculate_grade(obtained_marks, total_marks):
    """Grade letter from the marks. Call check_result_values first."""
    percentage = (float(obtained_marks) / float(total_marks)) * 100
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
    error = check_result_values(obtained_marks, total_marks, exam_type)
    if error:
        return jsonify({
            "message": error,
            "status": "failed"
        }), 400

    # A student has one midterm and one final per subject (quizzes and assignments can repeat)
    if exam_type in ['midterm', 'final']:
        existing = Result.query.filter_by(student_id=student_id, subject_id=subject_id, exam_type=exam_type).first()
        if existing:
            return jsonify({
                "message": f"This student already has a {exam_type} result in this subject. Edit that result instead.",
                "status": "failed"
            }), 409

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
        "student_id": result.student_id,
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
            "student_id": result.student_id,
            "total_marks": float(result.total_marks),
            "obtained_marks": float(result.obtained_marks),
            "grade": result.grade,
            "exam_type": result.exam_type,
            "remarks": result.remarks
        })
    return jsonify(results_list)

def get_results_by_student(student_id):
    results = Result.query.filter_by(student_id=student_id).all()
    results_list = []
    for result in results:
        results_list.append({
            "id": result.id,
            "subject_name": result.subject.name,
            "student_name": result.student.name,
            "student_id": result.student_id,
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

    # Check the new values together with the ones that are not changing
    obtained_marks = kwargs.get('obtained_marks', result.obtained_marks)
    total_marks = kwargs.get('total_marks', result.total_marks)
    exam_type = kwargs.get('exam_type', result.exam_type)
    error = check_result_values(obtained_marks, total_marks, exam_type)
    if error:
        return jsonify({
            "message": error,
            "status": "failed"
        }), 400

    for key, value in kwargs.items():
        if hasattr(result, key):
            setattr(result, key, value)

    if 'obtained_marks' in kwargs or 'total_marks' in kwargs:
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