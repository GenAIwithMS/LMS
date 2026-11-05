from src.models import Student,Enrollment
from src.services.users import is_email_taken, is_username_taken
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from src.db import db



def student_data(student):
    """What the API shows about a student."""
    section = student.section
    return {
        "id": student.id,
        "name": student.name,
        "username": student.username,
        "section_id": student.section_id,
        "section_name": section.name if section else None,
        "section_full_name": section.full_name() if section else None,
        "class_id": section.class_id if section else None,
        "email": student.email,
        "roll_number": student.roll_number,
        "admission_number": student.admission_number,
        "guardian_name": student.guardian_name,
        "guardian_phone": student.guardian_phone,
        "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
    }


def is_admission_number_taken(admission_number, current_student=None):
    """Admission numbers are unique across the school."""
    if not admission_number:
        return False
    other = Student.query.filter_by(admission_number=admission_number).first()
    return other is not None and other is not current_student


def roll_number_clash(section_id, roll_number, current_student=None):
    """A message if another student of the section already has this roll number, otherwise None.
    Roll numbers only need to be different inside one section (5-A and 5-B can both have roll 1)."""
    if not roll_number or not section_id:
        return None
    roll_number = str(roll_number).strip()
    for other in Student.query.filter_by(section_id=section_id).all():
        if other is current_student:
            continue
        if other.roll_number and other.roll_number.strip() == roll_number:
            section_name = other.section.full_name() if other.section else "this section"
            return f"Roll number {roll_number} is already used in {section_name} by {other.name}"
    return None


def add_students(name, username, section, password, email, roll_number=None, admission_number=None,
                 guardian_name=None, guardian_phone=None, date_of_birth=None):
    if is_email_taken(email):
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    if is_username_taken(username):
        return jsonify({
            "message":"Username already exists",
            "status":"failed"
        }), 400
    if is_admission_number_taken(admission_number):
        return jsonify({
            "message":"Admission number already exists",
            "status":"failed"
        }), 400
    clash = roll_number_clash(section, roll_number)
    if clash:
        return jsonify({
            "message": clash,
            "status": "failed"
        }), 400
    
    new_student = Student(
        name=name,
        username=username,
        section_id=section,
        email=email,
        roll_number=roll_number,
        admission_number=admission_number or None,
        guardian_name=guardian_name,
        guardian_phone=guardian_phone,
        date_of_birth=date_of_birth,
    )


    new_student.set_password(password)
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({
        "message":"student added successfully",
        "status":"success"
    }), 201

def get_all_students():
    # No students yet is not an error: the list is simply empty
    students = Student.query.all()
    
    student_list = []
    for student in students:
        student_list.append(student_data(student))
    return jsonify(student_list)

def get_student_by_id(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({
            "message":"student not found",
            "status":"failed"
        }), 404
    
    return jsonify({
        "student": student_data(student)
    })


def update_student(student_id, **kwargs):

    student = Student.query.get(student_id)

    if not student:
        return jsonify({
            "message":"student not found",
            "status":"failed"
        }), 400
    
    if "email" in kwargs and is_email_taken(kwargs["email"], current_user=student):
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    if "admission_number" in kwargs and is_admission_number_taken(kwargs["admission_number"], current_student=student):
        return jsonify({
            "message":"Admission number already exists",
            "status":"failed"
        }), 400
    if "username" in kwargs and is_username_taken(kwargs["username"], current_user=student):
        return jsonify({
            "message":"Username already exists",
            "status":"failed"
        }), 400

    # The roll number must still be free in the (possibly new) section
    new_section_id = student.section_id
    if kwargs.get("section_id"):
        new_section_id = kwargs["section_id"]
    new_roll_number = student.roll_number
    if kwargs.get("roll_number"):
        new_roll_number = kwargs["roll_number"]
    clash = roll_number_clash(new_section_id, new_roll_number, current_student=student)
    if clash:
        return jsonify({
            "message": clash,
            "status": "failed"
        }), 400

    for key, value in kwargs.items():
        if value is None:
            continue
        if key == 'password':
            student.set_password(value)
        elif hasattr(student, key):
            setattr(student, key, value)

    db.session.commit()
    
    return jsonify({
        "message":"student updated successfully",
        "status":"success"
    })

def delete_student(student_id, remove_records=False):
    """Delete a student. If they still have marks, attendance or submissions, only when
    remove_records is True (see services/delete_checks.py)."""
    # Imported here, not at the top: delete_checks imports from this package (a circular import)
    from src.services.delete_checks import delete_student_with_records
    return delete_student_with_records(student_id, remove_records)