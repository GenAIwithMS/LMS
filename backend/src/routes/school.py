from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from marshmallow import ValidationError
from src.schemas import (ClassSectionSchema, UpdateClassSectionSchema, SubjectTeacherSchema, ClassSubjectSchema,
                         ChapterSchema, UpdateChapterSchema, AcademicSessionSchema, TeacherSubjectSchema, UpdateAcademicSessionSchema)
from src.services.school import (get_all_classes, get_class_details, add_class_section, edit_class_section,
                                 remove_class_section, get_section_details, set_subject_teacher, add_class_subject,
                                 rename_class_subject, remove_class_subject, get_subject_chapters, add_subject_chapter,
                                 edit_subject_chapter, remove_subject_chapter, get_all_sessions, add_session,
                                 set_current_session, get_teacher_classes, get_student_class, get_teacher_subject_list,
                                 add_teacher_subject, remove_teacher_subject, edit_session, delete_session)
from src.services.access import get_teacher_section_ids, get_teacher_subject_ids
from src.models import Subject, Student

# The school structure: Classes 1-10, their sections and class incharges, each
# class's subjects and chapters, and who teaches each subject in each section.
# The admin sets it all up. Teachers and students can read their own part.

school_bp = Blueprint("school", __name__)


def only_admin():
    """An error answer if the user is not the admin, otherwise None."""
    if get_jwt().get("role") != "admin":
        return jsonify({"message": "Only the admin can change the school structure", "status": "failed"}), 403
    return None


# ---------------- Classes

@school_bp.route("/api/school/classes", methods=["GET"])
@jwt_required()
def list_classes():
    return get_all_classes()


@school_bp.route("/api/school/classes/<int:class_id>", methods=["GET"])
@jwt_required()
def class_details(class_id):
    return get_class_details(class_id)


# ---------------- Sections

@school_bp.route("/api/school/classes/<int:class_id>/sections", methods=["POST"])
@jwt_required()
def create_section(class_id):
    error = only_admin()
    if error:
        return error
    try:
        data = ClassSectionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return add_class_section(class_id, data["name"], data.get("incharge_id"))


@school_bp.route("/api/school/sections/<int:section_id>", methods=["GET"])
@jwt_required()
def section_details(section_id):
    token = get_jwt()
    # A teacher can open the sections they lead or teach in
    if token.get("role") == "teacher":
        teacher_id = int(get_jwt_identity())
        if section_id not in get_teacher_section_ids(teacher_id):
            return jsonify({"message": "You don't teach in this section", "status": "failed"}), 403
    elif token.get("role") != "admin":
        return jsonify({"message": "Only teachers and the admin can open a section", "status": "failed"}), 403
    return get_section_details(section_id)


@school_bp.route("/api/school/sections/<int:section_id>", methods=["PUT"])
@jwt_required()
def update_section(section_id):
    error = only_admin()
    if error:
        return error
    try:
        data = UpdateClassSectionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_class_section(section_id, data)


@school_bp.route("/api/school/sections/<int:section_id>", methods=["DELETE"])
@jwt_required()
def delete_section(section_id):
    error = only_admin()
    if error:
        return error
    return remove_class_section(section_id)


@school_bp.route("/api/school/sections/<int:section_id>/teachers", methods=["PUT"])
@jwt_required()
def choose_subject_teacher(section_id):
    error = only_admin()
    if error:
        return error
    try:
        data = SubjectTeacherSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return set_subject_teacher(section_id, data["subject_id"], data["teacher_id"])


# ---------------- Subjects and chapters (the syllabus)

@school_bp.route("/api/school/classes/<int:class_id>/subjects", methods=["POST"])
@jwt_required()
def create_subject(class_id):
    error = only_admin()
    if error:
        return error
    try:
        data = ClassSubjectSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return add_class_subject(class_id, data["name"])


@school_bp.route("/api/school/subjects/<int:subject_id>", methods=["PUT"])
@jwt_required()
def update_subject(subject_id):
    error = only_admin()
    if error:
        return error
    try:
        data = ClassSubjectSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return rename_class_subject(subject_id, data["name"])


@school_bp.route("/api/school/subjects/<int:subject_id>", methods=["DELETE"])
@jwt_required()
def delete_subject(subject_id):
    error = only_admin()
    if error:
        return error
    return remove_class_subject(subject_id)


@school_bp.route("/api/school/subjects/<int:subject_id>/chapters", methods=["GET"])
@jwt_required()
def list_chapters(subject_id):
    token = get_jwt()
    # The syllabus is visible to the admin, the subject's teachers, and students of that class
    if token.get("role") == "teacher":
        teacher_id = int(get_jwt_identity())
        if subject_id not in get_teacher_subject_ids(teacher_id):
            return jsonify({"message": "You don't teach this subject", "status": "failed"}), 403
    elif token.get("role") == "student":
        student = Student.query.get(int(get_jwt_identity()))
        subject = Subject.query.get(subject_id)
        if not student or not subject or not student.section or student.section.class_id != subject.class_id:
            return jsonify({"message": "This subject is not in your class", "status": "failed"}), 403
    return get_subject_chapters(subject_id)


@school_bp.route("/api/school/subjects/<int:subject_id>/chapters", methods=["POST"])
@jwt_required()
def create_chapter(subject_id):
    error = only_admin()
    if error:
        return error
    try:
        data = ChapterSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return add_subject_chapter(subject_id, data["title"], data.get("description"), data.get("number"))


@school_bp.route("/api/school/chapters/<int:chapter_id>", methods=["PUT"])
@jwt_required()
def update_chapter(chapter_id):
    error = only_admin()
    if error:
        return error
    try:
        data = UpdateChapterSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_subject_chapter(chapter_id, data)


@school_bp.route("/api/school/chapters/<int:chapter_id>", methods=["DELETE"])
@jwt_required()
def delete_chapter(chapter_id):
    error = only_admin()
    if error:
        return error
    return remove_subject_chapter(chapter_id)


# ---------------- Academic sessions

@school_bp.route("/api/school/sessions", methods=["GET"])
@jwt_required()
def list_sessions():
    return get_all_sessions()


@school_bp.route("/api/school/sessions", methods=["POST"])
@jwt_required()
def create_session():
    error = only_admin()
    if error:
        return error
    try:
        data = AcademicSessionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return add_session(data["name"], data["start_date"], data["end_date"], data.get("is_current", False))


@school_bp.route("/api/school/sessions/<int:session_id>", methods=["PUT"])
@jwt_required()
def update_session(session_id):
    error = only_admin()
    if error:
        return error
    try:
        data = UpdateAcademicSessionSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return edit_session(session_id, data)


@school_bp.route("/api/school/sessions/<int:session_id>", methods=["DELETE"])
@jwt_required()
def remove_session(session_id):
    error = only_admin()
    if error:
        return error
    return delete_session(session_id)


@school_bp.route("/api/school/sessions/<int:session_id>/current", methods=["PUT"])
@jwt_required()
def make_session_current(session_id):
    error = only_admin()
    if error:
        return error
    return set_current_session(session_id)


# ---------------- A teacher's or student's own classes

@school_bp.route("/api/school/my-classes", methods=["GET"])
@jwt_required()
def my_classes():
    if get_jwt().get("role") != "teacher":
        return jsonify({"message": "Only teachers have classes to teach", "status": "failed"}), 403
    return get_teacher_classes(int(get_jwt_identity()))


@school_bp.route("/api/school/my-class", methods=["GET"])
@jwt_required()
def my_class():
    if get_jwt().get("role") != "student":
        return jsonify({"message": "Only students have a class", "status": "failed"}), 403
    return get_student_class(int(get_jwt_identity()))


# ---------------- The subjects each teacher can teach (set before giving them any class)

@school_bp.route("/api/school/teacher-subjects", methods=["GET"])
@jwt_required()
def teacher_subjects():
    error = only_admin()
    if error:
        return error
    return get_teacher_subject_list()


@school_bp.route("/api/school/teachers/<int:teacher_id>/subjects", methods=["POST"])
@jwt_required()
def give_teacher_subject(teacher_id):
    error = only_admin()
    if error:
        return error
    try:
        data = TeacherSubjectSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    return add_teacher_subject(teacher_id, data["name"])


@school_bp.route("/api/school/teachers/<int:teacher_id>/subjects", methods=["DELETE"])
@jwt_required()
def take_teacher_subject(teacher_id):
    error = only_admin()
    if error:
        return error
    name = request.args.get("name", "")
    if name.strip() == "":
        return jsonify({"message": "Say which subject to remove (?name=Urdu)", "status": "failed"}), 400
    return remove_teacher_subject(teacher_id, name)
