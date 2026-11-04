from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from marshmallow import ValidationError
from src.models import ExamTerm, ExamPaper, TeachingAssignment
from src.schemas import (ExamTermSchema, UpdateExamTermSchema, ClassPapersSchema, UpdatePaperSchema, PaperReviewSchema,
                         PaperMarksSchema, ReportRemarksSchema, PromotionSchema, GradeScaleSchema)
from src.services.access import teacher_teaches, teacher_is_incharge, get_teacher_section_ids
from src.services.exam import (get_all_terms, get_term, add_term, edit_term, delete_term, get_term_papers, set_up_class_papers,
                               edit_paper, delete_paper, get_teacher_papers, save_question_file, get_question_file_path,
                               review_question_file)
from src.services.exam_results import (get_section_paper_marks, save_section_paper_marks, get_section_result_sheet,
                                       get_report_card, find_report_card_section_id, save_report_remarks,
                                       get_student_report_cards, get_term_analysis)
from src.services.promotion import get_promotion_list, promote_students
from src.services.grading import get_grade_scale, save_grade_scale, reset_grade_scale

# Exams:
# - the admin sets up terms and papers, reviews question papers, locks and publishes
#   results, sees the analysis, and promotes students at the end of the session
# - a subject teacher uploads the question paper and enters marks for their sections
# - the class incharge writes the report card remarks
# - a student opens their own report card once the term is published

exam_bp = Blueprint("exam", __name__)


def current_user():
    """The role and ID of the logged-in user."""
    return get_jwt().get("role"), int(get_jwt_identity())


def only_admin():
    """An error answer if the user is not the admin, otherwise None."""
    if get_jwt().get("role") != "admin":
        return jsonify({"message": "Only the admin can do this", "status": "failed"}), 403
    return None


def teacher_teaches_subject_anywhere(teacher_id, subject_id):
    """True if the teacher teaches this subject in at least one section."""
    teaching = TeachingAssignment.query.filter_by(teacher_id=teacher_id, subject_id=subject_id).first()
    return teaching is not None


# ---------------- Terms

@exam_bp.route("/api/exams/terms", methods=["GET"])
@jwt_required()
def list_terms():
    role, user_id = current_user()
    # Students only see terms whose results are published
    if role == "student":
        return get_student_report_cards(user_id)
    return get_all_terms(request.args.get("session_id", type=int))


@exam_bp.route("/api/exams/terms/<int:term_id>", methods=["GET"])
@jwt_required()
def term_details(term_id):
    role, user_id = current_user()
    if role == "student":
        term = ExamTerm.query.get(term_id)
        if not term or not term.is_published:
            return jsonify({"message": "Exam term not found", "status": "failed"}), 404
    return get_term(term_id)


@exam_bp.route("/api/exams/terms", methods=["POST"])
@jwt_required()
def create_term():
    error = only_admin()
    if error:
        return error
    try:
        data = ExamTermSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return add_term(data["session_id"], data["name"], data["start_date"], data["end_date"], data.get("marks_deadline"))


@exam_bp.route("/api/exams/terms/<int:term_id>", methods=["PUT"])
@jwt_required()
def update_term(term_id):
    error = only_admin()
    if error:
        return error
    try:
        data = UpdateExamTermSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_term(term_id, data)


@exam_bp.route("/api/exams/terms/<int:term_id>", methods=["DELETE"])
@jwt_required()
def remove_term(term_id):
    error = only_admin()
    if error:
        return error
    return delete_term(term_id)


# ---------------- Papers

@exam_bp.route("/api/exams/terms/<int:term_id>/papers", methods=["GET"])
@jwt_required()
def list_papers(term_id):
    error = only_admin()
    if error:
        return error
    return get_term_papers(term_id, request.args.get("class_id", type=int))


@exam_bp.route("/api/exams/terms/<int:term_id>/papers", methods=["POST"])
@jwt_required()
def create_class_papers(term_id):
    error = only_admin()
    if error:
        return error
    try:
        data = ClassPapersSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return set_up_class_papers(term_id, data["class_id"], data.get("total_marks"), data.get("passing_marks"))


@exam_bp.route("/api/exams/papers/<int:paper_id>", methods=["PUT"])
@jwt_required()
def update_paper(paper_id):
    error = only_admin()
    if error:
        return error
    try:
        data = UpdatePaperSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_paper(paper_id, data)


@exam_bp.route("/api/exams/papers/<int:paper_id>", methods=["DELETE"])
@jwt_required()
def remove_paper(paper_id):
    error = only_admin()
    if error:
        return error
    return delete_paper(paper_id)


@exam_bp.route("/api/exams/terms/<int:term_id>/my-papers", methods=["GET"])
@jwt_required()
def my_papers(term_id):
    role, user_id = current_user()
    if role != "teacher":
        return jsonify({"message": "Only teachers have papers to mark", "status": "failed"}), 403
    return get_teacher_papers(user_id, term_id)


# ---------------- Question papers

@exam_bp.route("/api/exams/papers/<int:paper_id>/question-paper", methods=["POST"])
@jwt_required()
def upload_question_paper(paper_id):
    role, user_id = current_user()
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404
    if role != "teacher" or not teacher_teaches_subject_anywhere(user_id, paper.subject_id):
        return jsonify({"message": "Only a teacher of this subject can upload its question paper", "status": "failed"}), 403

    file = request.files.get("file")
    if not file:
        return jsonify({"message": "Choose a PDF file to upload", "status": "failed"}), 400
    return save_question_file(paper_id, file, user_id)


@exam_bp.route("/api/exams/papers/<int:paper_id>/question-paper", methods=["GET"])
@jwt_required()
def download_question_paper(paper_id):
    role, user_id = current_user()
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404

    # Students never see a question paper before the exam
    allowed = role == "admin"
    if role == "teacher" and teacher_teaches_subject_anywhere(user_id, paper.subject_id):
        allowed = True
    if not allowed:
        return jsonify({"message": "You can't open this question paper", "status": "failed"}), 403

    path, download_name = get_question_file_path(paper)
    if not path:
        return jsonify({"message": "No question paper has been uploaded yet", "status": "failed"}), 404
    return send_file(path, as_attachment=True, download_name=download_name, mimetype="application/pdf")


@exam_bp.route("/api/exams/papers/<int:paper_id>/review", methods=["PUT"])
@jwt_required()
def review_question_paper(paper_id):
    error = only_admin()
    if error:
        return error
    try:
        data = PaperReviewSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return review_question_file(paper_id, data["approve"], data.get("note"))


# ---------------- Marks

@exam_bp.route("/api/exams/papers/<int:paper_id>/sections/<int:section_id>/marks", methods=["GET"])
@jwt_required()
def paper_marks(paper_id, section_id):
    role, user_id = current_user()
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404

    # The admin, the subject teacher of the section and its class incharge can see the marks
    allowed = role == "admin"
    if role == "teacher":
        if teacher_teaches(user_id, section_id, paper.subject_id) or teacher_is_incharge(user_id, section_id):
            allowed = True
    if not allowed:
        return jsonify({"message": "You can't see these marks", "status": "failed"}), 403
    return get_section_paper_marks(paper_id, section_id)


@exam_bp.route("/api/exams/papers/<int:paper_id>/sections/<int:section_id>/marks", methods=["PUT"])
@jwt_required()
def enter_paper_marks(paper_id, section_id):
    role, user_id = current_user()
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({"message": "Paper not found", "status": "failed"}), 404
    if role != "teacher" or not teacher_teaches(user_id, section_id, paper.subject_id):
        return jsonify({"message": "Only the teacher of this subject in this section can enter its marks", "status": "failed"}), 403

    try:
        data = PaperMarksSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return save_section_paper_marks(paper_id, section_id, data["marks"], user_id)


# ---------------- Results and report cards

@exam_bp.route("/api/exams/terms/<int:term_id>/sections/<int:section_id>/results", methods=["GET"])
@jwt_required()
def section_result_sheet(term_id, section_id):
    role, user_id = current_user()
    allowed = role == "admin"
    if role == "teacher" and section_id in get_teacher_section_ids(user_id):
        allowed = True
    if not allowed:
        return jsonify({"message": "You can't see this section's results", "status": "failed"}), 403
    return get_section_result_sheet(term_id, section_id)


@exam_bp.route("/api/exams/terms/<int:term_id>/students/<int:student_id>/report-card", methods=["GET"])
@jwt_required()
def report_card(term_id, student_id):
    role, user_id = current_user()

    allowed = False
    if role == "admin":
        allowed = True
    if role == "teacher":
        section_id = find_report_card_section_id(term_id, student_id)
        if section_id and section_id in get_teacher_section_ids(user_id):
            allowed = True
    if role == "student" and student_id == user_id:
        term = ExamTerm.query.get(term_id)
        if not term or not term.is_published:
            return jsonify({"message": "This report card hasn't been published yet", "status": "failed"}), 403
        allowed = True
    if not allowed:
        return jsonify({"message": "You can't see this report card", "status": "failed"}), 403
    return get_report_card(term_id, student_id)


@exam_bp.route("/api/exams/terms/<int:term_id>/students/<int:student_id>/remarks", methods=["PUT"])
@jwt_required()
def write_remarks(term_id, student_id):
    role, user_id = current_user()
    section_id = find_report_card_section_id(term_id, student_id)
    if role != "teacher" or not section_id or not teacher_is_incharge(user_id, section_id):
        return jsonify({"message": "Only the class incharge writes report card remarks", "status": "failed"}), 403
    try:
        data = ReportRemarksSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return save_report_remarks(term_id, student_id, data["remarks"], user_id)


@exam_bp.route("/api/exams/terms/<int:term_id>/analysis", methods=["GET"])
@jwt_required()
def term_analysis(term_id):
    error = only_admin()
    if error:
        return error
    return get_term_analysis(term_id, request.args.get("class_id", type=int))


# ---------------- Promotion

@exam_bp.route("/api/exams/promotion/sections/<int:section_id>", methods=["GET"])
@jwt_required()
def promotion_list(section_id):
    error = only_admin()
    if error:
        return error
    return get_promotion_list(section_id, request.args.get("term_id", type=int))


@exam_bp.route("/api/exams/promotion/sections/<int:section_id>", methods=["POST"])
@jwt_required()
def promote(section_id):
    error = only_admin()
    if error:
        return error
    try:
        data = PromotionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return promote_students(section_id, data["target_section_id"], data["student_ids"])


# ---------------- Grading scale (each school can use its own)

@exam_bp.route("/api/exams/grading-scale", methods=["GET"])
@jwt_required()
def grading_scale():
    return get_grade_scale()


@exam_bp.route("/api/exams/grading-scale", methods=["PUT"])
@jwt_required()
def change_grading_scale():
    error = only_admin()
    if error:
        return error
    try:
        data = GradeScaleSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return save_grade_scale(data["bands"])


@exam_bp.route("/api/exams/grading-scale/reset", methods=["POST"])
@jwt_required()
def reset_grading_scale():
    error = only_admin()
    if error:
        return error
    return reset_grade_scale()
