from decimal import Decimal
from flask import jsonify
from src.db import db, pakistan_time
from src.models import ExamTerm, ExamPaper, ExamMark, ReportRemark, Section, Student, DailyAttendance, TeachingAssignment
from src.services.exam import term_is_closed, marks_text, paper_data, term_data
from src.services.daily_attendance import count_statuses
from src.services.grading import grade_for, scale_data
from src.services.wording import plural


# Exam results: subject teachers enter marks for their sections, then the school
# gets report cards (with each student's position in the section), result sheets
# for a whole section, and an analysis by class, subject and teacher.

# Grades come from the school's grading scale (services/grading.py), which the admin can change.


def percentage_of(obtained, total):
    if total is None or total == 0:
        return None
    return round(float(obtained) * 100 / float(total), 1)


# ---------------- Marks entry

def section_term_students(term, section):
    """The students of a section for a term's results: those whose marks were entered
    in this section, plus (in the current session) everyone in the section now."""
    students = []
    student_ids = []

    papers = ExamPaper.query.filter_by(term_id=term.id, class_id=section.class_id).all()
    for paper in papers:
        for mark in paper.marks:
            if mark.section_id == section.id and mark.student_id not in student_ids:
                student_ids.append(mark.student_id)
                students.append(mark.student)

    if term.session.is_current:
        for student in Student.query.filter_by(section_id=section.id).all():
            if student.id not in student_ids:
                student_ids.append(student.id)
                students.append(student)

    students.sort(key=lambda student: (student.roll_number or "", student.name))
    return students


def get_section_paper_marks(paper_id, section_id):
    """A paper's marks sheet for one section: every student with their marks (or absent)."""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404
    section = Section.query.get(section_id)
    if not section or section.class_id != paper.class_id:
        return jsonify({"message": "This section is not in the paper's class", "status": "failed"}), 400

    student_list = []
    for student in section_term_students(paper.term, section):
        mark = ExamMark.query.filter_by(paper_id=paper.id, student_id=student.id).first()
        obtained = None
        is_absent = False
        if mark:
            obtained = marks_text(mark.obtained_marks)
            is_absent = mark.is_absent
        student_list.append({
            "student_id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "obtained_marks": obtained,
            "is_absent": is_absent
        })

    data = paper_data(paper)
    data["section_id"] = section.id
    data["section_name"] = section.full_name()
    data["is_closed"] = term_is_closed(paper.term)
    data["students"] = student_list
    return jsonify(data)


def save_section_paper_marks(paper_id, section_id, rows, teacher_id):
    """rows: [{"student_id", "obtained_marks" (number or None), "is_absent"}].
    A row with no marks that isn't absent is left as it is."""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404
    section = Section.query.get(section_id)
    if not section or section.class_id != paper.class_id:
        return jsonify({"message": "This section is not in the paper's class", "status": "failed"}), 400

    if term_is_closed(paper.term):
        return jsonify({"message": f"Marks for {paper.term.name} are locked", "status": "failed"}), 403

    # Check everything first, so nothing is saved if one row is wrong
    for row in rows:
        student = Student.query.get(row["student_id"])
        if not student or student.section_id != section.id:
            return jsonify({"message": f"Student {row['student_id']} is not in {section.full_name()}", "status": "failed"}), 400
        obtained = row.get("obtained_marks")
        if not row.get("is_absent") and obtained is not None:
            if obtained < 0 or obtained > paper.total_marks:
                return jsonify({"message": f"{student.name}'s marks must be between 0 and {marks_text(paper.total_marks)}", "status": "failed"}), 400

    saved = 0
    for row in rows:
        is_absent = row.get("is_absent", False)
        obtained = row.get("obtained_marks")
        if not is_absent and obtained is None:
            continue
        if is_absent:
            obtained = None

        mark = ExamMark.query.filter_by(paper_id=paper.id, student_id=row["student_id"]).first()
        if not mark:
            mark = ExamMark(paper_id=paper.id, student_id=row["student_id"])
            db.session.add(mark)
        mark.section_id = section.id
        mark.obtained_marks = obtained
        mark.is_absent = is_absent
        mark.entered_by = teacher_id
        saved = saved + 1
    db.session.commit()

    return jsonify({"message": f"Marks saved for {plural(saved, 'student')}", "status": "success"})


# ---------------- Report cards and result sheets

def student_term_result(student, papers):
    """One student's marks in every paper, the totals, and whether they passed."""
    subject_list = []
    total_marks = Decimal("0")
    total_obtained = Decimal("0")
    missing = 0
    failed = 0

    for paper in papers:
        mark = ExamMark.query.filter_by(paper_id=paper.id, student_id=student.id).first()
        total_marks = total_marks + paper.total_marks

        obtained = None
        is_absent = False
        passed = None
        if mark:
            is_absent = mark.is_absent
            if mark.is_absent:
                passed = False
            else:
                obtained = mark.obtained_marks
                total_obtained = total_obtained + mark.obtained_marks
                passed = mark.obtained_marks >= paper.passing_marks
        else:
            missing = missing + 1

        if passed is False:
            failed = failed + 1

        subject_percentage = None
        if obtained is not None:
            subject_percentage = percentage_of(obtained, paper.total_marks)

        subject_list.append({
            "paper_id": paper.id,
            "subject_id": paper.subject_id,
            "subject_name": paper.subject.name,
            "total_marks": marks_text(paper.total_marks),
            "passing_marks": marks_text(paper.passing_marks),
            "obtained_marks": marks_text(obtained),
            "is_absent": is_absent,
            "percentage": subject_percentage,
            "grade": grade_for(subject_percentage),
            "passed": passed
        })

    percentage = None
    if len(papers) > 0 and missing < len(papers):
        percentage = percentage_of(total_obtained, total_marks)

    # Pass only when every subject is marked and passed
    if failed > 0:
        result = "Fail"
    elif missing > 0:
        result = "Incomplete"
    else:
        result = "Pass"

    return {
        "student_id": student.id,
        "name": student.name,
        "roll_number": student.roll_number,
        "subjects": subject_list,
        "total_marks": marks_text(total_marks),
        "total_obtained": marks_text(total_obtained),
        "percentage": percentage,
        "grade": grade_for(percentage),
        "result": result,
        "position": None
    }


def add_positions(results):
    """Rank the students by total marks, highest first. Equal totals share a position (1, 2, 2, 4).

    Only students whose marks are all in get a position; while marks are still missing
    ("Incomplete") a position would be misleading.
    """
    ranked = []
    for item in results:
        if item["percentage"] is not None and item["result"] != "Incomplete":
            ranked.append(item)
    ranked.sort(key=lambda item: Decimal(item["total_obtained"]), reverse=True)

    position = 0
    previous_total = None
    for index, item in enumerate(ranked):
        total = Decimal(item["total_obtained"])
        if total != previous_total:
            position = index + 1
            previous_total = total
        item["position"] = position


def section_results(term, section):
    """Every student's result in the section for the term, with positions."""
    papers = ExamPaper.query.filter_by(term_id=term.id, class_id=section.class_id).all()
    papers.sort(key=lambda paper: paper.subject.name)

    results = []
    for student in section_term_students(term, section):
        results.append(student_term_result(student, papers))
    add_positions(results)
    return results, papers


def get_section_result_sheet(term_id, section_id):
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    results, papers = section_results(term, section)

    subject_list = []
    for paper in papers:
        subject_list.append({"paper_id": paper.id, "subject_name": paper.subject.name, "total_marks": marks_text(paper.total_marks)})

    passed = 0
    for item in results:
        if item["result"] == "Pass":
            passed = passed + 1

    return jsonify({
        "term": term_data(term),
        "section_id": section.id,
        "section_name": section.full_name(),
        "incharge_name": section.teacher.name if section.teacher else None,
        "subjects": subject_list,
        "students": results,
        "passed_count": passed
    })


def find_student_term_section(term, student):
    """The section a student sat the term's exams in (it may differ from today's after promotion)."""
    papers = ExamPaper.query.filter_by(term_id=term.id).all()
    for paper in papers:
        mark = ExamMark.query.filter_by(paper_id=paper.id, student_id=student.id).first()
        if mark:
            return Section.query.get(mark.section_id)
    return student.section


def term_attendance(term, student):
    """The student's daily attendance from the start to the end of the term (or today)."""
    last_day = term.end_date
    today = pakistan_time().date()
    if today < last_day:
        last_day = today

    records = []
    for record in DailyAttendance.query.filter_by(student_id=student.id).all():
        if record.date >= term.start_date and record.date <= last_day:
            records.append(record)
    return count_statuses(records)


def get_report_card(term_id, student_id):
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found", "status": "failed"}), 404

    section = find_student_term_section(term, student)
    if not section or not section.class_id:
        return jsonify({"message": "This student isn't in a class", "status": "failed"}), 400

    results, papers = section_results(term, section)
    card = None
    for item in results:
        if item["student_id"] == student.id:
            card = item
    if card is None:
        card = student_term_result(student, papers)

    remark = ReportRemark.query.filter_by(term_id=term.id, student_id=student.id).first()

    card["term"] = term_data(term)
    card["section_id"] = section.id
    card["section_name"] = section.full_name()
    card["class_strength"] = len(results)
    card["incharge_name"] = section.teacher.name if section.teacher else None
    card["admission_number"] = student.admission_number
    card["guardian_name"] = student.guardian_name
    card["attendance"] = term_attendance(term, student)
    card["remarks"] = remark.remarks if remark else None
    card["grade_scale"] = scale_data()
    return jsonify(card)


def find_report_card_section_id(term_id, student_id):
    """The section ID used for a student's report card in a term (for permission checks)."""
    term = ExamTerm.query.get(term_id)
    student = Student.query.get(student_id)
    if not term or not student:
        return None
    section = find_student_term_section(term, student)
    if not section:
        return None
    return section.id


def save_report_remarks(term_id, student_id, remarks, teacher_id):
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404
    if term.is_published:
        return jsonify({"message": "This term's report cards are already published", "status": "failed"}), 403

    remark = ReportRemark.query.filter_by(term_id=term_id, student_id=student_id).first()
    remarks = remarks.strip()
    if remarks == "":
        if remark:
            db.session.delete(remark)
            db.session.commit()
        return jsonify({"message": "Remarks removed", "status": "success"})

    if remark:
        remark.remarks = remarks
        remark.written_by = teacher_id
    else:
        db.session.add(ReportRemark(term_id=term_id, student_id=student_id, remarks=remarks, written_by=teacher_id))
    db.session.commit()
    return jsonify({"message": "Remarks saved", "status": "success"})


def get_student_report_cards(student_id):
    """The published terms a student can open a report card for."""
    term_list = []
    terms = ExamTerm.query.filter_by(is_published=True).order_by(ExamTerm.start_date.desc()).all()
    for term in terms:
        term_list.append(term_data(term))
    return jsonify(term_list)


# ---------------- Analysis

def get_term_analysis(term_id, class_id=None):
    """For each section: each subject's average, pass rate, highest marks and teacher,
    and the top students. Then each teacher's subjects across sections."""
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404

    class_ids = []
    for paper in ExamPaper.query.filter_by(term_id=term_id).all():
        if paper.class_id not in class_ids:
            class_ids.append(paper.class_id)
    if class_id:
        class_ids = [class_id]

    section_list = []
    teacher_rows = {}
    for one_class_id in sorted(class_ids):
        sections = Section.query.filter_by(class_id=one_class_id).order_by(Section.name).all()
        for section in sections:
            results, papers = section_results(term, section)

            subject_rows = []
            for paper_index, paper in enumerate(papers):
                percentages = []
                passed = 0
                highest = None
                for item in results:
                    subject = item["subjects"][paper_index]
                    if subject["passed"] is None:
                        continue
                    if subject["passed"]:
                        passed = passed + 1
                    if subject["percentage"] is not None:
                        percentages.append(subject["percentage"])
                    else:
                        percentages.append(0)     # absent counts as 0
                    if subject["obtained_marks"] is not None:
                        obtained = Decimal(subject["obtained_marks"])
                        if highest is None or obtained > highest:
                            highest = obtained

                average = None
                pass_rate = None
                if len(percentages) > 0:
                    average = round(sum(percentages) / len(percentages), 1)
                    pass_rate = round(passed * 100 / len(percentages), 1)

                teaching = TeachingAssignment.query.filter_by(section_id=section.id, subject_id=paper.subject_id).first()
                teacher_name = teaching.teacher.name if teaching else None

                row = {
                    "subject_name": paper.subject.name,
                    "teacher_name": teacher_name,
                    "marked_count": len(percentages),
                    "average_percentage": average,
                    "pass_percentage": pass_rate,
                    "highest_marks": marks_text(highest),
                    "total_marks": marks_text(paper.total_marks)
                }
                subject_rows.append(row)

                if teaching:
                    if teaching.teacher_id not in teacher_rows:
                        teacher_rows[teaching.teacher_id] = {"teacher_name": teacher_name, "subjects": []}
                    teacher_rows[teaching.teacher_id]["subjects"].append({
                        "section_name": section.full_name(),
                        "subject_name": paper.subject.name,
                        "average_percentage": average,
                        "pass_percentage": pass_rate
                    })

            top_students = []
            ranked = []
            for item in results:
                if item["position"] is not None:
                    ranked.append(item)
            ranked.sort(key=lambda item: item["position"])
            for item in ranked[:3]:
                top_students.append({"name": item["name"], "position": item["position"], "percentage": item["percentage"]})

            passed_students = 0
            for item in results:
                if item["result"] == "Pass":
                    passed_students = passed_students + 1

            section_list.append({
                "section_id": section.id,
                "section_name": section.full_name(),
                "student_count": len(results),
                "passed_count": passed_students,
                "subjects": subject_rows,
                "top_students": top_students
            })

    teacher_list = []
    for teacher_id in teacher_rows:
        teacher_list.append(teacher_rows[teacher_id])
    teacher_list.sort(key=lambda item: item["teacher_name"])

    return jsonify({
        "term": term_data(term),
        "sections": section_list,
        "teachers": teacher_list
    })
