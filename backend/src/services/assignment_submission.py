from src.models import AssignmentSubmission,Assignment,Student
from src.db import db
from flask import jsonify
from werkzeug.utils import secure_filename
import os
import uuid

# Uploaded files are kept outside the "static" folder, so nobody can download them
# without logging in. They are only served through /api/submission/file.
BACKEND_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_FOLDER = os.path.join(BACKEND_FOLDER, "uploads", "submissions")

# Where older versions of the LMS saved files (publicly served). Only used to find old files.
OLD_UPLOAD_FOLDER = os.path.join(BACKEND_FOLDER, "src", "static", "submissions")

ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "txt", "ppt", "pptx", "xls", "xlsx", "zip", "png", "jpg", "jpeg"]


def is_allowed_file(filename):
    """Check the file extension is one we accept."""
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def save_submission_file(file):
    """Save an uploaded file safely. Returns (saved_name, None) or (None, error message).

    secure_filename removes things like "../" so a file can't be written outside the
    upload folder. The random prefix stops two files with the same name overwriting each other.
    """
    original_name = secure_filename(file.filename or "")
    if not original_name or not is_allowed_file(original_name):
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        return None, f"File type not allowed. Allowed types: {allowed}"

    saved_name = f"{uuid.uuid4().hex}_{original_name}"

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file.save(os.path.join(UPLOAD_FOLDER, saved_name))
    return saved_name, None


def get_submission_file_path(submission):
    """Return the full path of a submission's file on disk, or None if there is no file."""
    if not submission.submission_file:
        return None

    filename = os.path.basename(submission.submission_file)

    new_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(new_path):
        return new_path

    old_path = os.path.join(OLD_UPLOAD_FOLDER, filename)
    if os.path.exists(old_path):
        return old_path

    return None


def submit_assignment(student_id, assignment_id, submission_text=None, submission_file=None,submitted_at=None,feedback=None):

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({
            "message": "Assignment not found",
            "status": "failed"
        }), 404

    saved_name = None
    if submission_file:
        saved_name, error = save_submission_file(submission_file)
        if error:
            return jsonify({
                "message": error,
                "status": "failed"
            }), 400

    new_submission = AssignmentSubmission(
        student_id=student_id,
        assignment_id=assignment_id,
        submission_text=submission_text,
        submission_file=saved_name,
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
        submissions = AssignmentSubmission.query.filter_by(student_id=student_id).all()
        
        if not submissions:
            return jsonify({
                "data": [],
                "status": "success"
            })
        
        assignment_ids = list(set([sub.assignment_id for sub in submissions]))
        
        assignments = Assignment.query.filter(Assignment.id.in_(assignment_ids)).all()
        assignment_dict = {assignment.id: assignment.title for assignment in assignments}
        
        submission_list = []
        for submission in submissions:
            assignment_title = assignment_dict.get(submission.assignment_id, f"Assignment {submission.assignment_id}")
            
            submitted_at_str = None
            if submission.submitted_at:
                try:
                    submitted_at_str = submission.submitted_at.isoformat()
                except Exception as e:
                    print(f"Error converting date for submission {submission.id}: {e}")
                    submitted_at_str = str(submission.submitted_at)
            
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
                "marks_obtained": marks_value,  
                "feedback": submission.feedback or "",
            }
            submission_list.append(submission_data)
        
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
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
        
        if not submissions:
            return jsonify({
                "data": [],
                "status": "success"
            })
        
        student_ids = list(set([sub.student_id for sub in submissions if sub.student_id]))
        
        student_dict = {}
        if student_ids:
            try:
                if len(student_ids) == 1:
                    student = Student.query.get(student_ids[0])
                    if student:
                        student_dict[student_ids[0]] = student.name
                else:
                    students = Student.query.filter(Student.id.in_(tuple(student_ids))).all()
                    student_dict = {student.id: student.name for student in students}
            except Exception as e:
                print(f"Error fetching students with batch query: {e}")
                import traceback
                print(traceback.format_exc())
                for student_id in student_ids:
                    try:
                        student = Student.query.get(student_id)
                        if student:
                            student_dict[student_id] = student.name
                    except Exception as e2:
                        print(f"Error fetching student {student_id}: {e2}")
        
        submission_list = []
        for submission in submissions:
            student_name = student_dict.get(submission.student_id, f"Student {submission.student_id}")
            
            submitted_at_str = None
            if submission.submitted_at:
                try:
                    submitted_at_str = submission.submitted_at.isoformat()
                except Exception as e:
                    print(f"Error converting date for submission {submission.id}: {e}")
                    submitted_at_str = str(submission.submitted_at)
            
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
                "marks_obtained": marks_value,  
                "feedback": submission.feedback or "",
            }
            submission_list.append(submission_data)
        
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