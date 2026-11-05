import os
import uuid
from decimal import Decimal
from flask import jsonify
from werkzeug.utils import secure_filename
from src.db import db, pakistan_time
from src.models import ExamTerm, ExamPaper, ExamMark, ReportRemark, AcademicSession, SchoolClass, Subject, Section, TeachingAssignment
from src.services.wording import plural


# Exams: the admin adds a term (like "First Term") to a session, then sets up the
# papers for each class (one paper per subject, with total and passing marks).
# The subject teacher uploads the question paper; the admin approves it or sends it back.

# Question papers are kept outside any public folder, like assignment files
BACKEND_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUESTION_PAPER_FOLDER = os.path.join(BACKEND_FOLDER, "uploads", "question_papers")

DEFAULT_TOTAL_MARKS = 100
DEFAULT_PASSING_MARKS = 33     # pass mark used by most Pakistani schools and boards


def marks_text(value):
    """Marks as text like "33" or "8.5", or None when empty."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


def term_is_closed(term):
    """True when marks can no longer change: the admin locked the term, or its deadline has passed."""
    if term.is_locked:
        return True
    if term.marks_deadline and pakistan_time().date() > term.marks_deadline:
        return True
    return False


# ---------------- Terms

def term_data(term):
    return {
        "id": term.id,
        "session_id": term.session_id,
        "session_name": term.session.name,
        "name": term.name,
        "start_date": term.start_date.isoformat(),
        "end_date": term.end_date.isoformat(),
        "marks_deadline": term.marks_deadline.isoformat() if term.marks_deadline else None,
        "is_locked": term.is_locked,
        "is_closed": term_is_closed(term),
        "is_published": term.is_published,
        "paper_count": ExamPaper.query.filter_by(term_id=term.id).count()
    }


def get_all_terms(session_id=None):
    """Terms, newest first. Without a session, every session's terms."""
    query = ExamTerm.query
    if session_id:
        query = query.filter_by(session_id=session_id)
    terms = query.order_by(ExamTerm.start_date.desc()).all()

    term_list = []
    for term in terms:
        term_list.append(term_data(term))
    return jsonify(term_list)


def get_term(term_id):
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404
    return jsonify(term_data(term))


def check_term_dates(start_date, end_date, marks_deadline):
    """An error message if the dates don't make sense, otherwise None."""
    if end_date < start_date:
        return "The term must end on or after the day it starts"
    if marks_deadline and marks_deadline < start_date:
        return "The marks deadline can't be before the term starts"
    return None


def add_term(session_id, name, start_date, end_date, marks_deadline=None):
    session = AcademicSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found", "status": "failed"}), 404

    name = name.strip()
    if ExamTerm.query.filter_by(session_id=session_id, name=name).first():
        return jsonify({"message": f"{session.name} already has a term called {name}", "status": "failed"}), 409

    problem = check_term_dates(start_date, end_date, marks_deadline)
    if problem:
        return jsonify({"message": problem, "status": "failed"}), 400

    term = ExamTerm(session_id=session_id, name=name, start_date=start_date, end_date=end_date,
                    marks_deadline=marks_deadline, is_locked=False, is_published=False)
    db.session.add(term)
    db.session.commit()
    return jsonify({"message": f"{name} added to {session.name}", "status": "success", "term": term_data(term)}), 201


def edit_term(term_id, data):
    """data can hold name, start_date, end_date, marks_deadline, is_locked and is_published."""
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404

    if "name" in data:
        new_name = data["name"].strip()
        other = ExamTerm.query.filter_by(session_id=term.session_id, name=new_name).first()
        if other and other.id != term.id:
            return jsonify({"message": f"This session already has a term called {new_name}", "status": "failed"}), 409
        term.name = new_name

    start_date = data.get("start_date", term.start_date)
    end_date = data.get("end_date", term.end_date)
    marks_deadline = term.marks_deadline
    if "marks_deadline" in data:
        marks_deadline = data["marks_deadline"]
    problem = check_term_dates(start_date, end_date, marks_deadline)
    if problem:
        return jsonify({"message": problem, "status": "failed"}), 400
    term.start_date = start_date
    term.end_date = end_date
    term.marks_deadline = marks_deadline

    if "is_locked" in data:
        term.is_locked = data["is_locked"]
    if "is_published" in data:
        term.is_published = data["is_published"]

    db.session.commit()
    return jsonify({"message": f"{term.name} updated", "status": "success", "term": term_data(term)})


def delete_term(term_id):
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404

    # Don't lose marks: refuse while any were entered
    for paper in ExamPaper.query.filter_by(term_id=term_id).all():
        if ExamMark.query.filter_by(paper_id=paper.id).count() > 0:
            return jsonify({"message": "Marks have already been entered for this term, so it can't be deleted", "status": "failed"}), 409

    for paper in ExamPaper.query.filter_by(term_id=term_id).all():
        remove_question_file(paper)
        db.session.delete(paper)
    ReportRemark.query.filter_by(term_id=term_id).delete()
    db.session.delete(term)
    db.session.commit()
    return jsonify({"message": "Exam term deleted", "status": "success"})


# ---------------- Papers

def paper_data(paper):
    return {
        "id": paper.id,
        "term_id": paper.term_id,
        "term_name": paper.term.name,
        "class_id": paper.class_id,
        "class_name": paper.school_class.name,
        "subject_id": paper.subject_id,
        "subject_name": paper.subject.name,
        "total_marks": marks_text(paper.total_marks),
        "passing_marks": marks_text(paper.passing_marks),
        "exam_date": paper.exam_date.isoformat() if paper.exam_date else None,
        "has_question_file": paper.question_file is not None,
        "question_status": paper.question_status,
        "review_note": paper.review_note,
        "uploaded_by": paper.uploader.name if paper.uploader else None,
        "marks_entered": ExamMark.query.filter_by(paper_id=paper.id).count()
    }


def get_term_papers(term_id, class_id=None):
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404

    query = ExamPaper.query.filter_by(term_id=term_id)
    if class_id:
        query = query.filter_by(class_id=class_id)
    papers = query.all()

    paper_list = []
    for paper in papers:
        paper_list.append(paper_data(paper))
    paper_list.sort(key=lambda item: (item["class_id"], item["subject_name"]))
    return jsonify(paper_list)


def set_up_class_papers(term_id, class_id, total_marks=None, passing_marks=None):
    """Add a paper for every subject of the class that doesn't have one in this term yet."""
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404
    school_class = SchoolClass.query.get(class_id)
    if not school_class:
        return jsonify({"message": "Class not found", "status": "failed"}), 404

    if total_marks is None:
        total_marks = DEFAULT_TOTAL_MARKS
    if passing_marks is None:
        passing_marks = DEFAULT_PASSING_MARKS
    if passing_marks > total_marks:
        return jsonify({"message": "Passing marks can't be more than the total", "status": "failed"}), 400

    subjects = Subject.query.filter_by(class_id=class_id).all()
    if len(subjects) == 0:
        return jsonify({"message": f"{school_class.name} has no subjects yet", "status": "failed"}), 400

    added = 0
    for subject in subjects:
        if ExamPaper.query.filter_by(term_id=term_id, subject_id=subject.id).first():
            continue
        db.session.add(ExamPaper(term_id=term_id, class_id=class_id, subject_id=subject.id,
                                 total_marks=total_marks, passing_marks=passing_marks, question_status="none"))
        added = added + 1
    db.session.commit()

    if added == 0:
        message = f"Every subject of {school_class.name} already has a paper"
    else:
        message = f"{plural(added, 'paper')} added for {school_class.name}"
    return jsonify({"message": message, "status": "success", "added": added}), 201


def edit_paper(paper_id, data):
    """data can hold total_marks, passing_marks and exam_date."""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404

    total_marks = data.get("total_marks", paper.total_marks)
    passing_marks = data.get("passing_marks", paper.passing_marks)
    if passing_marks > total_marks:
        return jsonify({"message": "Passing marks can't be more than the total", "status": "failed"}), 400

    # Marks already entered must still fit
    for mark in paper.marks:
        if mark.obtained_marks is not None and mark.obtained_marks > total_marks:
            return jsonify({"message": "Some students already have more marks than the new total", "status": "failed"}), 400

    paper.total_marks = total_marks
    paper.passing_marks = passing_marks
    if "exam_date" in data:
        paper.exam_date = data["exam_date"]

    db.session.commit()
    return jsonify({"message": f"{paper.subject.name} paper updated", "status": "success"})


def delete_paper(paper_id):
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404
    if ExamMark.query.filter_by(paper_id=paper_id).count() > 0:
        return jsonify({"message": "Marks have already been entered for this paper, so it can't be deleted", "status": "failed"}), 409

    remove_question_file(paper)
    db.session.delete(paper)
    db.session.commit()
    return jsonify({"message": "Paper deleted", "status": "success"})


def get_teacher_papers(teacher_id, term_id):
    """The papers this teacher marks in a term: one row per section where they teach the subject."""
    term = ExamTerm.query.get(term_id)
    if not term:
        return jsonify({"message": "Exam term not found", "status": "failed"}), 404

    row_list = []
    for teaching in TeachingAssignment.query.filter_by(teacher_id=teacher_id).all():
        paper = ExamPaper.query.filter_by(term_id=term_id, subject_id=teaching.subject_id).first()
        if not paper:
            continue
        section = Section.query.get(teaching.section_id)
        student_ids = []
        for student in section.students:
            student_ids.append(student.id)
        entered = 0
        for mark in paper.marks:
            if mark.section_id == section.id or mark.student_id in student_ids:
                entered = entered + 1

        row = paper_data(paper)
        row["section_id"] = section.id
        row["section_name"] = section.full_name()
        row["student_count"] = len(student_ids)
        row["marks_entered"] = entered
        row_list.append(row)

    row_list.sort(key=lambda item: (item["section_name"], item["subject_name"]))
    return jsonify({
        "term": term_data(term),
        "papers": row_list
    })


# ---------------- Question paper files

def remove_question_file(paper):
    if paper.question_file:
        path = os.path.join(QUESTION_PAPER_FOLDER, os.path.basename(paper.question_file))
        if os.path.exists(path):
            os.remove(path)
        paper.question_file = None


def save_question_file(paper_id, file, teacher_id):
    """The subject teacher uploads the question paper (PDF). It then waits for the admin's review."""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404

    if paper.question_status == "approved":
        return jsonify({"message": "The admin has already approved this question paper", "status": "failed"}), 409

    original_name = secure_filename(file.filename or "")
    if not original_name.lower().endswith(".pdf"):
        return jsonify({"message": "The question paper must be a PDF file", "status": "failed"}), 400

    # A real PDF starts with "%PDF"; this stops other files renamed to .pdf
    first_bytes = file.stream.read(4)
    file.stream.seek(0)
    if first_bytes != b"%PDF":
        return jsonify({"message": "This file is not a real PDF", "status": "failed"}), 400

    if not os.path.exists(QUESTION_PAPER_FOLDER):
        os.makedirs(QUESTION_PAPER_FOLDER)

    remove_question_file(paper)
    saved_name = f"{uuid.uuid4().hex}_{original_name}"
    file.save(os.path.join(QUESTION_PAPER_FOLDER, saved_name))

    paper.question_file = saved_name
    paper.question_status = "submitted"
    paper.review_note = None
    paper.uploaded_by = teacher_id
    db.session.commit()
    return jsonify({"message": "Question paper sent to the admin for review", "status": "success"})


def get_question_file_path(paper):
    """The question paper's place on disk and the name to download it with, or (None, None)."""
    if not paper.question_file:
        return None, None
    saved_name = os.path.basename(paper.question_file)
    path = os.path.join(QUESTION_PAPER_FOLDER, saved_name)
    if not os.path.exists(path):
        return None, None
    # Saved as "<random id>_<original name>"; download with the original name
    download_name = saved_name
    if "_" in saved_name:
        download_name = saved_name.split("_", 1)[1]
    return path, download_name


def review_question_file(paper_id, approve, note=None):
    """The admin approves the question paper, or returns it to the teacher with a note."""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404
    if not paper.question_file:
        return jsonify({"message": "No question paper has been uploaded yet", "status": "failed"}), 400

    if approve:
        paper.question_status = "approved"
        paper.review_note = note
        message = f"{paper.subject.name} question paper approved"
    else:
        if not note:
            return jsonify({"message": "Write a note telling the teacher what to change", "status": "failed"}), 400
        paper.question_status = "returned"
        paper.review_note = note
        message = f"{paper.subject.name} question paper returned to the teacher"

    db.session.commit()
    return jsonify({"message": message, "status": "success"})
