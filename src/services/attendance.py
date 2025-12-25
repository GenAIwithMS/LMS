from src.models.attendance import Attendance
from src.db import db
from flask import jsonify


def mark_attend(student_id, subject_id, date, time, status):
    attendance_record = Attendance(
        student_id=student_id,
        subject_id=subject_id,
        date=date,
        time=time,
        status=status
    )
    db.session.add(attendance_record)
    db.session.commit()

    return jsonify({
        "message": "Attendance marked successfully",
        "status": "success"
    })

def get_attendance_by_student(student_id):
    id_student = Attendance.query.filter_by(student_id=student_id).all()
    if not id_student:
        return jsonify({
            "message": "Student not found",
            "status": "error"
        }), 400
    
    result = []
    for record in id_student:
        result.append({
            "id": record.id,
            "subject_id": record.subject_id,
            "date": record.date.isoformat(),
            "time": record.time.isoformat(),
            "status": record.status
        })
    return jsonify(result)

def get_attendance_by_subject(subject_id):
    subject_attendance = Attendance.query.filter_by(subject_id=subject_id).all()
    if not subject_attendance:
        return jsonify({
            "message": "No attendance records found for this subject",
            "status": "error"
        }), 400
    
    result = []
    for record in subject_attendance:
        result.append({
            "id": record.id,
            "student_id": record.student_id,
            "date": record.date.isoformat(),
            "time": record.time.isoformat(),
            "status": record.status
        })
    
    return jsonify(result)


def get_all_attendance():
    attendance_records = Attendance.query.all()
    result = []
    for record in attendance_records:
        result.append({
            "id": record.id,
            "student_id": record.student_id,
            "subject_id": record.subject_id,
            "date": record.date.isoformat(),
            "time": record.time.isoformat(),
            "status": record.status
        })
    return jsonify(result)

def update_attendance(attendance_id, **kwargs):
    attendance_record = Attendance.query.get(attendance_id)
    if not attendance_record:
        return jsonify({
            "message": "Attendance record not found",
            "status": "error"
        }), 400
    
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
        }), 400
    
    db.session.delete(attendance_record)
    db.session.commit()
    
    return jsonify({
        "message": "Attendance record deleted successfully",
        "status": "success"
    })

