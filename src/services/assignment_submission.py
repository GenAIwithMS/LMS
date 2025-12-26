from src.models.assignment_submission import AssignmentSubmission
from src.db import db
from flask import jsonify
import os

def submit_assignment(student_id, assignment_id, submission_text=None, submission_file=None,submitted_at=None,feedback=None):

    file = submission_file
    if file:
        filepath = f"src/static/submissions/{file.filename}"
        if not os.path.exists("src/static/submissions/"):
            os.makedirs("src/static/submissions/")
        file.save(filepath)
        # submission_file = filepath
    new_submission = AssignmentSubmission(
        student_id=student_id,
        assignment_id=assignment_id,
        submission_text=submission_text,
        submission_file=filepath if file else None,
        feedback=feedback,
    )
    if submitted_at:
        new_submission.submitted_at = submitted_at

    db.session.add(new_submission)
    db.session.commit()

    return jsonify({
        "message": "Assignment submitted successfully",
        "status": "success"
    }), 201

def get_submissions_by_student(student_id):
    submissions = AssignmentSubmission.query.filter_by(student_id=student_id).all()
    submission_list = []
    for submission in submissions:
        submission_data = {
            "id": submission.id,
            "assignment_id": submission.assignment_id,
            "submission_text": submission.submission_text,
            "submission_file": submission.submission_file,
            "submitted_at": submission.submitted_at,
            "feedback": submission.feedback,
        }
        submission_list.append(submission_data)
    return jsonify(submission_list)

def get_submissions_by_assignment(assignment_id):
    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
    submission_list = []
    for submission in submissions:
        submission_data = {
            "id": submission.id,
            "student_id": submission.student_id,
            "submission_text": submission.submission_text,
            "submission_file": submission.submission_file,
            "submitted_at": submission.submitted_at,
            "feedback": submission.feedback,
        }
        submission_list.append(submission_data)
    return jsonify(submission_list)

def update_submission(submission_id, **kwargs):
    submission = AssignmentSubmission.query.get(submission_id)
    if not submission:
        return jsonify({
            "message": "Submission not found",
            "status": "error"
        }), 400

    for key, value in kwargs.items():
        if hasattr(submission, key):
            setattr(submission, key, value)

    db.session.commit()

    return jsonify({
        "message": "Submission updated successfully",
        "status": "success"
    })

def delete_submission(submission_id):
    submission = AssignmentSubmission.query.get(submission_id)
    if not submission:
        return jsonify({
            "message": "Submission not found",
            "status": "error"
        }), 400

    db.session.delete(submission)
    db.session.commit()

    return jsonify({
        "message": "Submission deleted successfully",
        "status": "success"
    })