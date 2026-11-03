from src.models import Attendance,Student,Subject
from src.db import db, pakistan_time
from flask import jsonify


def mark_attend(student_id, subject_id, status):
    # Only one record per student, subject and day
    today = pakistan_time().date()
    records = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id).all()
    for record in records:
        if record.mark_at and record.mark_at.date() == today:
            return jsonify({
                "message": "Attendance is already marked for this student in this subject today. Edit that record instead.",
                "status": "failed"
            }), 409

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
    # No records yet is not an error: the list is simply empty
    id_student = Attendance.query.filter_by(student_id=student_id).all()
    
    result = []
    for record in id_student:
        student = Student.query.get(record.student_id)
        subject = Subject.query.get(record.subject_id)
        result.append({
            "id": record.id,
            "student_name": student.name if student else None,
            "student_id": record.student_id,
            "subject_name": subject.name if subject else None,
            "mark_at": record.mark_at,
            "status": record.status
        })
    return jsonify(result)

def get_attendance_by_subject(subject_id):
    # No records yet is not an error: the list is simply empty
    subject_attendance = Attendance.query.filter_by(subject_id=subject_id).all()
    
    result = []
    for record in subject_attendance:
        student = Student.query.get(record.student_id)
        subject = Subject.query.get(record.subject_id)
        result.append({
            "id": record.id,
            "student_name": student.name if student else None,
            "student_id": record.student_id,
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
            "student_id": record.student_id,
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

