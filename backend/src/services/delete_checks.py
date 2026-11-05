import os
from flask import jsonify
from src.db import db
from src.models import (Student, Teacher, Section, TeachingAssignment, TeacherSubject, Assignment, AssignmentSubmission,
                        Attendance, Result, Enrollment, Announcement, Course, Subject, DailyAttendance, ChapterProgress,
                        DiaryEntry, ClassTest, ClassTestMark, ExamPaper, ExamMark, ReportRemark)
from src.services.assignment_submission import get_submission_file_path
from src.services.wording import plural


# Before deleting a student or a teacher, say exactly what they still have.
#
# - A student's records (marks, attendance, submissions...) can be deleted together with
#   the student, but only when the admin has seen the list and confirmed it.
# - A teacher can only be deleted once their classes have gone to other teachers and nothing
#   they wrote (assignments, diary, tests, announcements) still belongs to students' records.
#   Small "who did it" notes (who marked attendance, who entered marks) are simply cleared.


# ---------------- Students

def student_record_queries(student_id):
    """Each kind of record a student can have: (label, plural label, query)."""
    return [
        ("exam mark", "exam marks", ExamMark.query.filter_by(student_id=student_id)),
        ("report card remark", "report card remarks", ReportRemark.query.filter_by(student_id=student_id)),
        ("day of attendance", "days of attendance", DailyAttendance.query.filter_by(student_id=student_id)),
        ("class test mark", "class test marks", ClassTestMark.query.filter_by(student_id=student_id)),
        ("assignment submission", "assignment submissions", AssignmentSubmission.query.filter_by(student_id=student_id)),
        ("old result", "old results", Result.query.filter_by(student_id=student_id)),
        ("old subject attendance record", "old subject attendance records", Attendance.query.filter_by(student_id=student_id)),
        ("old course enrollment", "old course enrollments", Enrollment.query.filter_by(student_id=student_id)),
    ]


def student_records(student_id):
    """[{"label": "2 exam marks", "count": 2}, ...] for the records the student has."""
    record_list = []
    for word, word_plural, query in student_record_queries(student_id):
        count = query.count()
        if count > 0:
            record_list.append({"label": plural(count, word, word_plural), "count": count})
    return record_list


def get_student_delete_check(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found", "status": "failed"}), 404
    return jsonify({"name": student.name, "records": student_records(student_id)})


def delete_student_with_records(student_id, remove_records):
    """Delete a student. With records, only when remove_records is True (the admin confirmed the list)."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found", "status": "failed"}), 404

    records = student_records(student_id)
    if len(records) > 0 and not remove_records:
        labels = []
        for record in records:
            labels.append(record["label"])
        return jsonify({
            "message": f"{student.name} still has " + ", ".join(labels) + ". Confirm to delete the student together with these records.",
            "status": "failed",
            "records": records
        }), 409

    # Uploaded files of their submissions go too
    for submission in AssignmentSubmission.query.filter_by(student_id=student_id).all():
        file_path = get_submission_file_path(submission)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    for word, word_plural, query in student_record_queries(student_id):
        query.delete(synchronize_session=False)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"{student.name} deleted", "status": "success"})


# ---------------- Teachers

def teacher_delete_blockers(teacher_id):
    """Plain sentences saying what must change before the teacher can be deleted."""
    blockers = []

    led = []
    for section in Section.query.filter_by(teacher_id=teacher_id).all():
        led.append(section.full_name())
    if len(led) > 0:
        blockers.append("leads " + ", ".join(led) + " as class incharge (choose another incharge on the class page)")

    taught = []
    for teaching in TeachingAssignment.query.filter_by(teacher_id=teacher_id).all():
        taught.append(f"{teaching.subject.name} in {teaching.section.full_name()}")
    if len(taught) > 0:
        blockers.append("teaches " + ", ".join(taught) + " (give these to other teachers in Teachers > Subjects or on the class page)")

    # Things they wrote that belong to students' records
    written = []
    counts = [
        (Assignment.query.filter_by(teacher_id=teacher_id).count(), "assignment"),
        (DiaryEntry.query.filter_by(teacher_id=teacher_id).count(), "diary entry"),
        (ClassTest.query.filter_by(teacher_id=teacher_id).count(), "class test"),
        (Announcement.query.filter_by(teacher_id=teacher_id).count(), "announcement"),
        (Course.query.filter_by(teacher_id=teacher_id).count(), "old course"),
        (Subject.query.filter_by(teacher_id=teacher_id).count(), "old subject"),
    ]
    for count, word in counts:
        if count > 0:
            if word == "diary entry":
                written.append(plural(count, word, "diary entries"))
            else:
                written.append(plural(count, word))
    if len(written) > 0:
        blockers.append("wrote " + ", ".join(written) + " that students' records still use")

    return blockers


def get_teacher_delete_check(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found", "status": "failed"}), 404
    blockers = teacher_delete_blockers(teacher_id)
    return jsonify({"name": teacher.name, "blockers": blockers, "can_delete": len(blockers) == 0})


def delete_teacher_checked(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found", "status": "failed"}), 404

    blockers = teacher_delete_blockers(teacher_id)
    if len(blockers) > 0:
        return jsonify({
            "message": f"{teacher.name} can't be deleted yet: " + "; ".join(blockers) + ".",
            "status": "failed",
            "blockers": blockers
        }), 409

    # Clear the small "who did it" notes, and their list of subjects
    DailyAttendance.query.filter_by(marked_by=teacher_id).update({"marked_by": None}, synchronize_session=False)
    ChapterProgress.query.filter_by(updated_by=teacher_id).update({"updated_by": None}, synchronize_session=False)
    ExamPaper.query.filter_by(uploaded_by=teacher_id).update({"uploaded_by": None}, synchronize_session=False)
    ExamMark.query.filter_by(entered_by=teacher_id).update({"entered_by": None}, synchronize_session=False)
    ReportRemark.query.filter_by(written_by=teacher_id).update({"written_by": None}, synchronize_session=False)
    TeacherSubject.query.filter_by(teacher_id=teacher_id).delete(synchronize_session=False)

    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": f"{teacher.name} deleted", "status": "success"})
