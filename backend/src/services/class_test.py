from decimal import Decimal
from flask import jsonify
from src.db import db, pakistan_time
from src.models import ClassTest, ClassTestMark, Section, Subject, Student, SyllabusChapter


# Class tests: short tests a subject teacher takes in their section (a quiz, a chapter
# test). The teacher enters each student's marks. They are not part of the term report card.


def marks_text(value):
    """Marks as text like "8.5", or None when empty."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        # 8.50 becomes "8.5", and 10.00 becomes "10"
        text = format(value.normalize(), "f")
        return text
    return str(value)


def test_data(test):
    marks_entered = 0
    total = Decimal("0")
    for mark in test.marks:
        if mark.obtained_marks is not None:
            marks_entered = marks_entered + 1
            total = total + mark.obtained_marks

    average = None
    if marks_entered > 0:
        average = round(float(total) / marks_entered, 1)

    return {
        "id": test.id,
        "title": test.title,
        "date": test.date.isoformat(),
        "total_marks": marks_text(test.total_marks),
        "section_id": test.section_id,
        "section_name": test.section.full_name(),
        "subject_id": test.subject_id,
        "subject_name": test.subject.name,
        "teacher_id": test.teacher_id,
        "teacher_name": test.teacher.name,
        "chapter_id": test.chapter_id,
        "chapter_title": test.chapter.title if test.chapter else None,
        "marks_entered": marks_entered,
        "average": average
    }


def add_class_test(section_id, subject_id, teacher_id, title, day, total_marks, chapter_id=None):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400

    if chapter_id:
        chapter = SyllabusChapter.query.get(chapter_id)
        if not chapter or chapter.subject_id != subject_id:
            return jsonify({"message": "This chapter is not part of the subject", "status": "failed"}), 400

    if total_marks <= 0:
        return jsonify({"message": "Total marks must be more than 0", "status": "failed"}), 400

    test = ClassTest(
        section_id=section_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        chapter_id=chapter_id,
        title=title.strip(),
        date=day,
        total_marks=total_marks
    )
    db.session.add(test)
    db.session.commit()
    return jsonify({"message": f"Test '{test.title}' added", "status": "success", "test": test_data(test)}), 201


def get_class_tests(section_id=None, subject_id=None, teacher_id=None):
    """Tests, newest first, filtered by any of section, subject and teacher."""
    query = ClassTest.query
    if section_id:
        query = query.filter_by(section_id=section_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    tests = query.order_by(ClassTest.date.desc(), ClassTest.id.desc()).all()

    test_list = []
    for test in tests:
        test_list.append(test_data(test))
    return jsonify(test_list)


def get_class_test_marks(test_id):
    """The test, with every student of the section and their marks (None if not entered)."""
    test = ClassTest.query.get(test_id)
    if not test:
        return jsonify({"message": "Test not found", "status": "failed"}), 404

    students = Student.query.filter_by(section_id=test.section_id).order_by(Student.roll_number, Student.name).all()

    student_list = []
    for student in students:
        mark = ClassTestMark.query.filter_by(test_id=test.id, student_id=student.id).first()
        student_list.append({
            "student_id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "obtained_marks": marks_text(mark.obtained_marks) if mark else None,
            # Marked absent: the row exists but has no marks (no row means not entered yet)
            "is_absent": mark is not None and mark.obtained_marks is None
        })

    data = test_data(test)
    data["students"] = student_list
    return jsonify(data)


def save_class_test_marks(test_id, marks):
    """marks is a list of {"student_id": .., "obtained_marks": number or None (absent)}."""
    test = ClassTest.query.get(test_id)
    if not test:
        return jsonify({"message": "Test not found", "status": "failed"}), 404

    # Marks only once the test has taken place
    if test.date > pakistan_time().date():
        return jsonify({"message": f"This test is on {test.date.isoformat()}; marks can be entered on or after that day", "status": "failed"}), 400

    # Check everything first, so nothing is saved if one row is wrong
    for row in marks:
        student = Student.query.get(row["student_id"])
        if not student or student.section_id != test.section_id:
            return jsonify({"message": f"Student {row['student_id']} is not in {test.section.full_name()}", "status": "failed"}), 400
        obtained = row.get("obtained_marks")
        if obtained is not None:
            if obtained < 0 or obtained > test.total_marks:
                return jsonify({"message": f"{student.name}'s marks must be between 0 and {marks_text(test.total_marks)}", "status": "failed"}), 400

    for row in marks:
        mark = ClassTestMark.query.filter_by(test_id=test.id, student_id=row["student_id"]).first()
        if mark:
            mark.obtained_marks = row.get("obtained_marks")
        else:
            db.session.add(ClassTestMark(test_id=test.id, student_id=row["student_id"], obtained_marks=row.get("obtained_marks")))
    db.session.commit()

    return jsonify({"message": "Marks saved", "status": "success"})


def edit_class_test(test_id, data):
    """data can hold "title", "date", "total_marks" and "chapter_id"."""
    test = ClassTest.query.get(test_id)
    if not test:
        return jsonify({"message": "Test not found", "status": "failed"}), 404

    if "total_marks" in data:
        if data["total_marks"] <= 0:
            return jsonify({"message": "Total marks must be more than 0", "status": "failed"}), 400
        # Marks already entered must still fit
        for mark in test.marks:
            if mark.obtained_marks is not None and mark.obtained_marks > data["total_marks"]:
                return jsonify({"message": "Some students already have more marks than the new total", "status": "failed"}), 400
        test.total_marks = data["total_marks"]

    if "chapter_id" in data:
        chapter_id = data["chapter_id"]
        if chapter_id:
            chapter = SyllabusChapter.query.get(chapter_id)
            if not chapter or chapter.subject_id != test.subject_id:
                return jsonify({"message": "This chapter is not part of the subject", "status": "failed"}), 400
        test.chapter_id = chapter_id

    if "title" in data:
        test.title = data["title"].strip()
    if "date" in data:
        test.date = data["date"]

    db.session.commit()
    return jsonify({"message": "Test updated", "status": "success"})


def delete_class_test(test_id):
    test = ClassTest.query.get(test_id)
    if not test:
        return jsonify({"message": "Test not found", "status": "failed"}), 404

    ClassTestMark.query.filter_by(test_id=test_id).delete()
    db.session.delete(test)
    db.session.commit()
    return jsonify({"message": "Test deleted", "status": "success"})


def get_student_class_tests(student_id):
    """The tests taken in a student's section, each with the student's own marks."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found", "status": "failed"}), 404

    # The student's own marks, loaded once
    marks_by_test = {}
    for mark in ClassTestMark.query.filter_by(student_id=student_id).all():
        marks_by_test[mark.test_id] = mark

    # This section's tests, and earlier tests the student has marks in (from before a promotion)
    tests = ClassTest.query.filter(
        (ClassTest.section_id == student.section_id) | (ClassTest.id.in_(list(marks_by_test.keys())))
    ).order_by(ClassTest.date.desc(), ClassTest.id.desc()).all()

    test_list = []
    for test in tests:
        mark = marks_by_test.get(test.id)
        data = test_data(test)
        data["my_marks"] = marks_text(mark.obtained_marks) if mark else None
        data["was_absent"] = mark is not None and mark.obtained_marks is None
        test_list.append(data)
    return jsonify(test_list)
