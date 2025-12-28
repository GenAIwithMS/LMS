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
        # Query submissions
        submissions = AssignmentSubmission.query.filter_by(student_id=student_id).all()
        
        if not submissions:
            return jsonify({
                "data": [],
                "status": "success"
            })
        
        # Get all unique assignment IDs
        assignment_ids = list(set([sub.assignment_id for sub in submissions]))
        
        # Fetch all assignments in one query to avoid N+1 problem
        assignments = Assignment.query.filter(Assignment.id.in_(assignment_ids)).all()
        assignment_dict = {assignment.id: assignment.title for assignment in assignments}
        
        submission_list = []
        for submission in submissions:
            # Get assignment title from dictionary, fallback if not found
            assignment_title = assignment_dict.get(submission.assignment_id, f"Assignment {submission.assignment_id}")
            
            # Handle date conversion safely
            submitted_at_str = None
            if submission.submitted_at:
                try:
                    submitted_at_str = submission.submitted_at.isoformat()
                except Exception as e:
                    print(f"Error converting date for submission {submission.id}: {e}")
                    submitted_at_str = str(submission.submitted_at)
            
            # Handle marks conversion safely
            marks_value = None
            if submission.marks is not None:
                try:
                    marks_value = float(submission.marks)
                except (ValueError, TypeError) as e:
                    print(f"Error converting marks for submission {submission.id}: {e}")
                    marks_value = None
            
            submission_data = {
                "id": submission.id,
                "assignment_id": submission.assignment_id,
                "assignment": assignment_title,
                "submission_text": submission.submission_text or "",
                "submission_file": submission.submission_file or "",
                "submitted_at": submitted_at_str,
                "marks": marks_value,
                "marks_obtained": marks_value,  # For API compatibility
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
        # Query submissions
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
        
        if not submissions:
            return jsonify({
                "data": [],
                "status": "success"
            })
        
        # Get all unique student IDs
        student_ids = list(set([sub.student_id for sub in submissions if sub.student_id]))
        
        # Fetch all students in one query to avoid N+1 problem
        student_dict = {}
        if student_ids:
            try:
                # Use tuple() for better compatibility with some database backends
                if len(student_ids) == 1:
                    # Single student - use get() for better performance
                    student = Student.query.get(student_ids[0])
                    if student:
                        student_dict[student_ids[0]] = student.name
                else:
                    # Multiple students - use IN clause
                    students = Student.query.filter(Student.id.in_(tuple(student_ids))).all()
                    student_dict = {student.id: student.name for student in students}
            except Exception as e:
                print(f"Error fetching students with batch query: {e}")
                import traceback
                print(traceback.format_exc())
                # Fallback: fetch students one by one if batch query fails
                for student_id in student_ids:
                    try:
                        student = Student.query.get(student_id)
                        if student:
                            student_dict[student_id] = student.name
                    except Exception as e2:
                        print(f"Error fetching student {student_id}: {e2}")
        
        submission_list = []
        for submission in submissions:
            # Get student name from dictionary, fallback if not found
            student_name = student_dict.get(submission.student_id, f"Student {submission.student_id}")
            
            # Handle date conversion safely
            submitted_at_str = None
            if submission.submitted_at:
                try:
                    submitted_at_str = submission.submitted_at.isoformat()
                except Exception as e:
                    print(f"Error converting date for submission {submission.id}: {e}")
                    submitted_at_str = str(submission.submitted_at)
            
            # Handle marks conversion safely
            marks_value = None
            if submission.marks is not None:
                try:
                    marks_value = float(submission.marks)
                except (ValueError, TypeError) as e:
                    print(f"Error converting marks for submission {submission.id}: {e}")
                    marks_value = None
            
            submission_data = {
                "id": submission.id,
                "student_id": submission.student_id,
                "student": student_name,
                "student_name": student_name,
                "submission_text": submission.submission_text or "",
                "submission_file": submission.submission_file or "",
                "submitted_at": submitted_at_str,
                "marks": marks_value,
                "marks_obtained": marks_value,  # For API compatibility
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