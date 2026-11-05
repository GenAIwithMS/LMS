from flask import jsonify
from src.db import db
from src.models import ExamTerm, Section, SchoolClass, Student
from src.services.exam_results import section_results
from src.services.school import section_summary


# Promotion at the end of the session: the admin moves the students who passed
# (usually in the Final term) from a section to a section of the next class.
# Students who are kept back simply stay where they are.


def get_promotion_list(section_id, term_id=None):
    """The section's students, each with their result in the term (if one is chosen),
    and the sections of the next class they can move to."""
    section = Section.query.get(section_id)
    if not section or not section.school_class:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    results_by_student = {}
    term = None
    if term_id:
        term = ExamTerm.query.get(term_id)
        if not term:
            return jsonify({"message": "Exam term not found", "status": "failed"}), 404
        results, papers = section_results(term, section)
        for item in results:
            results_by_student[item["student_id"]] = item

    student_list = []
    students = Student.query.filter_by(section_id=section_id).order_by(Student.roll_number, Student.name).all()
    for student in students:
        result = None
        percentage = None
        if student.id in results_by_student:
            result = results_by_student[student.id]["result"]
            percentage = results_by_student[student.id]["percentage"]
        student_list.append({
            "student_id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "result": result,
            "percentage": percentage,
            # Suggest promoting everyone who passed (or everyone, when no term is chosen)
            "suggest_promote": result == "Pass" or term is None
        })

    next_class = SchoolClass.query.filter_by(level=section.school_class.level + 1).first()
    target_list = []
    if next_class:
        for target in Section.query.filter_by(class_id=next_class.id).order_by(Section.name).all():
            target_list.append(section_summary(target))

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "class_name": section.school_class.name,
        "next_class_name": next_class.name if next_class else None,
        "is_last_class": next_class is None,
        "target_sections": target_list,
        "students": student_list
    })


def promote_students(section_id, target_section_id, student_ids):
    """Move these students from the section to a section of the next class."""
    section = Section.query.get(section_id)
    if not section or not section.school_class:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    target = Section.query.get(target_section_id)
    if not target or not target.school_class:
        return jsonify({"message": "Target section not found", "status": "failed"}), 404

    if target.school_class.level != section.school_class.level + 1:
        return jsonify({"message": f"Students of {section.school_class.name} can only move up to the next class", "status": "failed"}), 400

    if len(student_ids) == 0:
        return jsonify({"message": "Choose at least one student", "status": "failed"}), 400

    # Check everyone first, so nobody moves if one is wrong
    students = []
    for student_id in student_ids:
        student = Student.query.get(student_id)
        if not student or student.section_id != section.id:
            return jsonify({"message": f"Student {student_id} is not in {section.full_name()}", "status": "failed"}), 400
        students.append(student)

    # Keep each roll number only if it's still free in the new section
    taken = []
    for other in Student.query.filter_by(section_id=target.id).all():
        if other.roll_number:
            taken.append(other.roll_number.strip())
    cleared = 0
    for student in students:
        student.section_id = target.id
        if student.roll_number:
            roll = student.roll_number.strip()
            if roll in taken:
                student.roll_number = None
                cleared = cleared + 1
            else:
                taken.append(roll)
    db.session.commit()

    if len(students) == 1:
        message = f"1 student promoted to {target.full_name()}"
    else:
        message = f"{len(students)} students promoted to {target.full_name()}"
    if cleared == 1:
        message = message + ". 1 of them needs a new roll number (theirs was already used there)"
    if cleared > 1:
        message = message + f". {cleared} of them need new roll numbers (theirs were already used there)"
    return jsonify({"message": message, "status": "success", "roll_numbers_cleared": cleared})
