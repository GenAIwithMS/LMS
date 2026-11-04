from flask import jsonify
from src.db import db, pakistan_time
from src.models import DailyAttendance, Section, Student


# Daily attendance: once a day, the class incharge marks every student of their
# section as present, absent, late or on leave.

ATTENDANCE_STATUSES = ["present", "absent", "late", "leave"]


def count_statuses(records):
    """How many records have each status, and the attendance percentage.

    Late counts as attended. Leave is not counted against the student.
    """
    counts = {"present": 0, "absent": 0, "late": 0, "leave": 0}
    for record in records:
        if record.status in counts:
            counts[record.status] = counts[record.status] + 1

    days_counted = counts["present"] + counts["late"] + counts["absent"]
    if days_counted > 0:
        percentage = round((counts["present"] + counts["late"]) * 100 / days_counted, 1)
    else:
        percentage = None

    counts["total_days"] = len(records)
    counts["percentage"] = percentage
    return counts


def get_section_register(section_id, day):
    """Every student of the section, with their status on this day (None if not marked yet)."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    students = Student.query.filter_by(section_id=section_id).order_by(Student.roll_number, Student.name).all()

    student_list = []
    marked_count = 0
    for student in students:
        record = DailyAttendance.query.filter_by(student_id=student.id, date=day).first()
        status = None
        if record:
            status = record.status
            marked_count = marked_count + 1
        student_list.append({
            "student_id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "status": status
        })

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "incharge_id": section.teacher_id,
        "incharge_name": section.teacher.name if section.teacher else None,
        "date": day.isoformat(),
        "is_marked": len(students) > 0 and marked_count == len(students),
        "marked_count": marked_count,
        "students": student_list
    })


def save_section_register(section_id, day, records, teacher_id):
    """Save the day's attendance for the section. records is a list of
    {"student_id": .., "status": ..}. Marking the same day again updates it."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    if day > pakistan_time().date():
        return jsonify({"message": "Attendance can't be marked for a future date", "status": "failed"}), 400

    if len(records) == 0:
        return jsonify({"message": "No students were sent", "status": "failed"}), 400

    # Check everything first, so nothing is saved if one row is wrong
    for row in records:
        student = Student.query.get(row["student_id"])
        if not student or student.section_id != section_id:
            return jsonify({"message": f"Student {row['student_id']} is not in {section.full_name()}", "status": "failed"}), 400
        if row["status"] not in ATTENDANCE_STATUSES:
            return jsonify({"message": f"Unknown status '{row['status']}'", "status": "failed"}), 400

    for row in records:
        record = DailyAttendance.query.filter_by(student_id=row["student_id"], date=day).first()
        if record:
            record.status = row["status"]
            record.section_id = section_id
            record.marked_by = teacher_id
            record.marked_at = pakistan_time()
        else:
            db.session.add(DailyAttendance(
                section_id=section_id,
                student_id=row["student_id"],
                date=day,
                status=row["status"],
                marked_by=teacher_id
            ))
    db.session.commit()

    return jsonify({"message": f"Attendance saved for {section.full_name()} on {day.isoformat()}", "status": "success"})


def get_section_month_summary(section_id, year, month):
    """For each student of the section: how many days present, absent, late and on leave this month."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    students = Student.query.filter_by(section_id=section_id).order_by(Student.roll_number, Student.name).all()

    student_list = []
    for student in students:
        records = []
        for record in DailyAttendance.query.filter_by(student_id=student.id).all():
            if record.date.year == year and record.date.month == month:
                records.append(record)
        summary = count_statuses(records)
        summary["student_id"] = student.id
        summary["name"] = student.name
        summary["roll_number"] = student.roll_number
        student_list.append(summary)

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "month": f"{year}-{month:02d}",
        "students": student_list
    })


def get_student_daily_attendance(student_id):
    """A student's own attendance, newest day first, with totals."""
    records = DailyAttendance.query.filter_by(student_id=student_id).order_by(DailyAttendance.date.desc()).all()

    record_list = []
    for record in records:
        record_list.append({
            "id": record.id,
            "date": record.date.isoformat(),
            "status": record.status,
            "marked_by": record.teacher.name if record.teacher else None
        })

    return jsonify({
        "summary": count_statuses(records),
        "records": record_list
    })
