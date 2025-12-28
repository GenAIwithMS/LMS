from src.models.assignment_submission import AssignmentSubmission
from src.db import db
from flask import jsonify
from src.models.assignment import Assignment
from src.models.student import Student

import os

def submit_assignment(student_id, assignment_id, submission_text=None, submission_file=None,submitted_at=None,feedback=None):

    file = submission_file
    if file:
        filepath = f"src/static/submissions/{file.filename}"
        if not os.path.exists("src/static/submissions/"):
            os.makedirs("src/static/submissions/")
        file.save(filepath)
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
    try:
        # Query submissions without joinedload to avoid relationship issues
        submissions = AssignmentSubmission.query.filter_by(student_id=student_id).all()
        submission_list = []
        for submission in submissions:
            # Fetch assignment separately to avoid lazy loading issues
            try:
                assignment = Assignment.query.get(submission.assignment_id)
                assignment_title = assignment.title if assignment else f"Assignment {submission.assignment_id}"
            except Exception as e:
                print(f"Error fetching assignment {submission.assignment_id}: {e}")
                assignment_title = f"Assignment {submission.assignment_id}"
            
            submission_data = {
                "id": submission.id,
                "assignment_id": submission.assignment_id,
                "assignment": assignment_title,
                "submission_text": submission.submission_text or "",
                "submission_file": submission.submission_file or "",
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "marks": float(submission.marks) if submission.marks is not None else None,
                "marks_obtained": float(submission.marks) if submission.marks is not None else None,  # For API compatibility
                "feedback": submission.feedback or "",
            }
            submission_list.append(submission_data)
        
        # Return in a format consistent with other endpoints
        return jsonify({
            "data": submission_list,
            "status": "success"
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_submissions_by_student: {error_trace}")
        return jsonify({
            "message": f"Error fetching submissions: {str(e)}",
            "status": "error",
            "data": []
        }), 500

def get_submissions_by_assignment(assignment_id):
    try:
        # Query submissions without joinedload first to avoid relationship issues
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
        submission_list = []
        for submission in submissions:
            # Fetch student separately to avoid lazy loading issues
            try:
                student = Student.query.get(submission.student_id)
                student_name = student.name if student else f"Student {submission.student_id}"
            except Exception as e:
                print(f"Error fetching student {submission.student_id}: {e}")
                student_name = f"Student {submission.student_id}"
            
            submission_data = {
                "id": submission.id,
                "student_id": submission.student_id,
                "student": student_name,
                "student_name": student_name,
                "submission_text": submission.submission_text or "",
                "submission_file": submission.submission_file or "",
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "marks": float(submission.marks) if submission.marks is not None else None,
                "marks_obtained": float(submission.marks) if submission.marks is not None else None,  # For API compatibility
                "feedback": submission.feedback or "",
            }
            submission_list.append(submission_data)
        
        # Return in a format consistent with other endpoints
        return jsonify({
            "data": submission_list,
            "status": "success"
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_submissions_by_assignment: {error_trace}")
        return jsonify({
            "message": f"Error fetching submissions: {str(e)}",
            "status": "error",
            "data": []
        }), 500

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