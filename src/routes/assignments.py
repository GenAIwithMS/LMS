from src.services.assignment import create_assignment, get_assignment_by_id,get_all_assignments,edit_assignment,delete_assignment
from flask import Blueprint, request, jsonify

assignment_bp = Blueprint("assignment", __name__)

@assignment_bp.route("/api/create/assignments", methods=["POST"])
def create_assign():

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    subject_id = data.get("subject_id")
    student_id = data.get("student_id")
    total_marks = data.get("total_marks")

    result = create_assignment(title, description, student_id,due_date,subject_id,total_marks)
    return result

@assignment_bp.route("/api/get/assignments", methods=["GET"])
def get_assignments():
    assignment_id = request.args.get("id", type=int)
    if assignment_id:
        result = get_assignment_by_id(assignment_id)
    else:
        result = get_all_assignments()
    return result

@assignment_bp.route("/api/update/assignments/", methods=["PUT"])
def update_assignment():

    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result = edit_assignment(assignment_id, **data)
    return result

@assignment_bp.route("/api/delete/assignments/", methods=["DELETE"])
def delete_assig():

    assignment_id = request.args.get("id", type=int)
    if not assignment_id:
        return jsonify({
            "message": "Assignment ID is required",
            "status": "error"
        }), 400

    result = delete_assignment(assignment_id)
    return result