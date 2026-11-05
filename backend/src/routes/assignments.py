from src.services import add_assignment, get_assignment_by_id,get_all_assignments,edit_assignment,delete_assignment
from flask import Blueprint, request, jsonify
from src.schemas import assignmentSchema,UpdateAssignmentSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from src.models import Subject, Assignment, AssignmentSubmission
from src.db import pakistan_time
from src.services.access import find_teacher_subject, teacher_teaches, get_teacher_teaching, teacher_owns_assignment, get_teacher_assignment_ids, get_student_assignment_ids, filter_response_by_ids

assignment_bp = Blueprint("assignment", __name__)


def check_due_date(due_date):
    """A message if the due date is before today, else None."""
    if due_date is not None and due_date < pakistan_time().date():
        return "The due date is in the past; choose today or a later date"
    return None


def check_total_marks(total_marks):
    """A message if the total marks are not more than 0, else None."""
    if total_marks is not None and float(total_marks) <= 0:
        return "Total marks must be more than 0"
    return None

@assignment_bp.route("/api/create/assignments", methods=["POST"])
@jwt_required()
def create_assign():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can create assignment",
            "status":"failed"
        }),403
    
    try:
        data = assignmentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    subject_name = data.get("subject_name")
    teacher_id = int(get_jwt_identity())  
    total_marks = data.get("total_marks")

    problem = check_due_date(due_date)
    if not problem:
        problem = check_total_marks(total_marks)
    if problem:
        return jsonify({"message": problem, "status": "failed"}), 400

    subject = find_teacher_subject(teacher_id, subject_name, data.get("subject_id"))
    if not subject:
        return jsonify({
            "message": "Subject not found among the subjects you teach",
            "status": "failed"
        }), 400

    # The assignment is for one section where the teacher teaches this subject
    section_id = data.get("section_id")
    if section_id:
        if not teacher_teaches(teacher_id, section_id, subject.id):
            return jsonify({
                "message": f"You don't teach {subject.name} in this section",
                "status": "failed"
            }), 403
    else:
        teaching_sections = []
        for teaching in get_teacher_teaching(teacher_id):
            if teaching.subject_id == subject.id:
                teaching_sections.append(teaching.section_id)
        if len(teaching_sections) == 1:
            section_id = teaching_sections[0]
        else:
            return jsonify({
                "message": f"You teach {subject.name} in more than one section. Choose the section.",
                "status": "failed"
            }), 400

    result = add_assignment(title, description, teacher_id, due_date, subject.id, total_marks, section_id)
    return result

@assignment_bp.route("/api/get/assignments", methods=["GET"])
@jwt_required()
def get_assignments():
    token = get_jwt()
    user_role = token["role"]
    user_id = int(get_jwt_identity())

    assignment_id = request.args.get("id", type=int)
    if assignment_id:
        if user_role == "teacher" and not teacher_owns_assignment(user_id, assignment_id):
            return jsonify({
                "message": "You can only view your own assignments",
                "status": "failed"
            }), 403
        if user_role == "student" and assignment_id not in get_student_assignment_ids(user_id):
            return jsonify({
                "message": "Assignment not found",
                "status": "failed"
            }), 404
        result = get_assignment_by_id(assignment_id)
    else:
        result = get_all_assignments()
        # A teacher only sees their own assignments
        if user_role == "teacher":
            result = filter_response_by_ids(result, get_teacher_assignment_ids(user_id))
        # A student only sees assignments from teachers who teach them
        if user_role == "student":
            result = filter_response_by_ids(result, get_student_assignment_ids(user_id))
    return result

@assignment_bp.route("/api/update/assignments/", methods=["PUT"])
@jwt_required()
def update_assignment():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can update assignments",
            "status":"failed"
        }),403
    
    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400

    teacher_id = int(get_jwt_identity())
    if not teacher_owns_assignment(teacher_id, assignment_id):
        return jsonify({
            "message": "You can only update your own assignments",
            "status": "failed"
        }), 403

    try:
        data = UpdateAssignmentSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    assignment = Assignment.query.get(assignment_id)

    # A past due date is only refused when it is being changed (an old assignment can keep its date)
    if 'due_date' in data and data['due_date'] != assignment.due_date:
        problem = check_due_date(data['due_date'])
        if problem:
            return jsonify({"message": problem, "status": "failed"}), 400

    if 'total_marks' in data:
        problem = check_total_marks(data['total_marks'])
        if problem:
            return jsonify({"message": problem, "status": "failed"}), 400
        # The total can't go below marks already given
        for submission in AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all():
            if submission.marks is not None and float(submission.marks) > float(data['total_marks']):
                return jsonify({"message": "Some students already have more marks than the new total", "status": "failed"}), 400

    kwargs = {}
    for key, value in data.items():
        if key == 'subject_id' or key == 'subject_name':
            # The ID wins when both are sent
            if key == 'subject_name' and 'subject_id' in data:
                continue
            subject = find_teacher_subject(teacher_id, data.get('subject_name'), data.get('subject_id'))
            if not subject:
                return jsonify({"message": "Subject not found among the subjects you teach", "status": "failed"}), 400
            # The new subject must be one the teacher teaches in the assignment's section
            assignment = Assignment.query.get(assignment_id)
            if assignment.section_id and not teacher_teaches(teacher_id, assignment.section_id, subject.id):
                return jsonify({"message": f"You don't teach {subject.name} in this assignment's section", "status": "failed"}), 400
            kwargs['subject_id'] = subject.id
        else:
            kwargs[key] = value

    result = edit_assignment(assignment_id, **kwargs)
    return result

@assignment_bp.route("/api/delete/assignments/", methods=["DELETE"])
@jwt_required()
def delete_assig():

    token = get_jwt()
    if token["role"] != "teacher":
        return jsonify({
            "message":"only teachers can delete assignments",
            "status":"failed"
        }),403
    
    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400

    teacher_id = int(get_jwt_identity())
    if not teacher_owns_assignment(teacher_id, assignment_id):
        return jsonify({
            "message": "You can only delete your own assignments",
            "status": "failed"
        }), 403

    result = delete_assignment(assignment_id)
    return result