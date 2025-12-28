from src.models.attendance import Attendance
from src.models.student import Student
from src.models.subject import Subject
from src.db import db
from flask import jsonify


def mark_attend(student_id, subject_id, status):
    attendance_record = Attendance(
        student_id=student_id,
        subject_id=subject_id,

        status=status
    )
    db.session.add(attendance_record)
    db.session.commit()

    return jsonify({
        "message": "Attendance marked successfully",
        "status": "success"
    }), 201

def get_attendance_by_student(student_id):
    id_student = Attendance.query.filter_by(student_id=student_id).all()
    if not id_student:
        return jsonify({
            "message": "Student not found",
            "status": "error"
        }), 404
    
    result = []
    for record in id_student:
        student = Student.query.get(record.student_id)
        subject = Subject.query.get(record.subject_id)
        result.append({
            "id": record.id,
            "student_name": student.name if student else None,
            "subject_name": subject.name if subject else None,
            "mark_at": record.mark_at,
            "status": record.status
        })
    return jsonify(result)

def get_attendance_by_subject(subject_id):
    subject_attendance = Attendance.query.filter_by(subject_id=subject_id).all()
    if not subject_attendance:
        return jsonify({
            "message": "No attendance records found for this subject",
            "status": "error"
        }), 404
    
    result = []
    for record in subject_attendance:
        student = Student.query.get(record.student_id)
        subject = Subject.query.get(record.subject_id)
        result.append({
            "id": record.id,
            "student_name": student.name if student else None,
            "subject_name": subject.name if subject else None,
            "mark_at": record.mark_at,
            "status": record.status
        })
    
    return jsonify(result)


def get_all_attendance():
    attendance_records = Attendance.query.all()
    result = []
    for record in attendance_records:
        student = Student.query.get(record.student_id)
        subject = Subject.query.get(record.subject_id)
        result.append({
            "id": record.id,
            "student_name": student.name if student else None,
            "subject_name": subject.name if subject else None,
            "mark_at": record.mark_at,
            "status": record.status
        })
    return jsonify(result)

def update_attendance(attendance_id, **kwargs):
    attendance_record = Attendance.query.get(attendance_id)
    if not attendance_record:
        return jsonify({
            "message": "Attendance record not found",
            "status": "error"
        }), 404
    
    for key, value in kwargs.items():
        if hasattr(attendance_record, key):
            setattr(attendance_record, key, value)
    
    db.session.commit()
    
    return jsonify({
        "message": "Attendance record updated successfully",
        "status": "success"
    })

def delete_attendance(attendance_id):
    attendance_record = Attendance.query.get(attendance_id)
    if not attendance_record:
        return jsonify({
            "message": "Attendance record not found",
            "status": "error"
        }), 404
    
    db.session.delete(attendance_record)
    db.session.commit()
    
    return jsonify({
        "message": "Attendance record deleted successfully",
        "status": "success"
    })

