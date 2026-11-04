from flask import jsonify
from src.db import db
from src.models import (AcademicSession, SchoolClass, Section, Subject, SyllabusChapter, TeachingAssignment,
                        Teacher, Student, Assignment, Result, Attendance)


# ---------------- Classes 1 to 10

def make_sure_classes_exist():
    """Create Class 1 to Class 10 if any are missing (the migration also does this)."""
    added = False
    for level in range(1, 11):
        existing = SchoolClass.query.filter_by(level=level).first()
        if not existing:
            db.session.add(SchoolClass(id=level, name=f"Class {level}", level=level))
            added = True
    if added:
        db.session.commit()


def section_summary(section):
    """The short description of a section used in lists."""
    student_count = Student.query.filter_by(section_id=section.id).count()
    return {
        "id": section.id,
        "name": section.name,
        "full_name": section.full_name(),
        "class_id": section.class_id,
        "incharge_id": section.teacher_id,
        "incharge_name": section.teacher.name if section.teacher else None,
        "student_count": student_count
    }


def get_all_classes():
    make_sure_classes_exist()
    classes = SchoolClass.query.order_by(SchoolClass.level).all()

    class_list = []
    for school_class in classes:
        sections = Section.query.filter_by(class_id=school_class.id).order_by(Section.name).all()
        section_list = []
        for section in sections:
            section_list.append(section_summary(section))

        class_list.append({
            "id": school_class.id,
            "name": school_class.name,
            "level": school_class.level,
            "sections": section_list,
            "subject_count": Subject.query.filter_by(class_id=school_class.id).count()
        })
    return jsonify(class_list)


def get_class_details(class_id):
    school_class = SchoolClass.query.get(class_id)
    if not school_class:
        return jsonify({"message": "Class not found", "status": "failed"}), 404

    sections = Section.query.filter_by(class_id=class_id).order_by(Section.name).all()
    section_list = []
    for section in sections:
        section_list.append(section_summary(section))

    subjects = Subject.query.filter_by(class_id=class_id).order_by(Subject.name).all()
    subject_list = []
    for subject in subjects:
        subject_list.append({
            "id": subject.id,
            "name": subject.name,
            "chapter_count": SyllabusChapter.query.filter_by(subject_id=subject.id).count()
        })

    return jsonify({
        "id": school_class.id,
        "name": school_class.name,
        "level": school_class.level,
        "sections": section_list,
        "subjects": subject_list
    })


# ---------------- Sections

def add_class_section(class_id, name, incharge_id=None):
    school_class = SchoolClass.query.get(class_id)
    if not school_class:
        return jsonify({"message": "Class not found", "status": "failed"}), 404

    name = name.strip()
    if Section.query.filter_by(class_id=class_id, name=name).first():
        return jsonify({"message": f"{school_class.name} already has a section {name}", "status": "failed"}), 409

    if incharge_id and not Teacher.query.get(incharge_id):
        return jsonify({"message": "Teacher not found", "status": "failed"}), 400

    section = Section(name=name, class_id=class_id, teacher_id=incharge_id)
    db.session.add(section)
    db.session.commit()
    return jsonify({"message": f"Section {section.full_name()} added", "status": "success", "section_id": section.id}), 201


def edit_class_section(section_id, data):
    """data can hold "name" and "incharge_id" (None removes the incharge)."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    if "name" in data:
        new_name = data["name"].strip()
        other = Section.query.filter_by(class_id=section.class_id, name=new_name).first()
        if other and other.id != section.id:
            return jsonify({"message": f"This class already has a section {new_name}", "status": "failed"}), 409
        section.name = new_name

    if "incharge_id" in data:
        incharge_id = data["incharge_id"]
        if incharge_id and not Teacher.query.get(incharge_id):
            return jsonify({"message": "Teacher not found", "status": "failed"}), 400
        section.teacher_id = incharge_id

    db.session.commit()
    return jsonify({"message": "Section updated", "status": "success"})


def remove_class_section(section_id):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    if Student.query.filter_by(section_id=section_id).count() > 0:
        return jsonify({"message": "This section still has students. Move them to another section first.", "status": "failed"}), 409

    TeachingAssignment.query.filter_by(section_id=section_id).delete()
    db.session.delete(section)
    db.session.commit()
    return jsonify({"message": "Section deleted", "status": "success"})


def get_section_details(section_id):
    """The section with its class incharge, its students, and each subject with its teacher."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    students = Student.query.filter_by(section_id=section_id).order_by(Student.roll_number, Student.name).all()
    student_list = []
    for student in students:
        student_list.append({
            "id": student.id,
            "name": student.name,
            "username": student.username,
            "roll_number": student.roll_number
        })

    subject_list = []
    if section.class_id:
        subjects = Subject.query.filter_by(class_id=section.class_id).order_by(Subject.name).all()
        for subject in subjects:
            teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject.id).first()
            subject_list.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "teacher_id": teaching.teacher_id if teaching else None,
                "teacher_name": teaching.teacher.name if teaching else None
            })

    details = section_summary(section)
    details["class_name"] = section.school_class.name if section.school_class else None
    details["students"] = student_list
    details["subjects"] = subject_list
    return jsonify(details)


def set_subject_teacher(section_id, subject_id, teacher_id):
    """Choose who teaches a subject in a section. teacher_id None removes the teacher."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400

    teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject_id).first()

    if teacher_id is None:
        if teaching:
            db.session.delete(teaching)
            db.session.commit()
        return jsonify({"message": f"{subject.name} in {section.full_name()} has no teacher now", "status": "success"})

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found", "status": "failed"}), 400

    if teaching:
        teaching.teacher_id = teacher.id
    else:
        db.session.add(TeachingAssignment(section_id=section_id, subject_id=subject_id, teacher_id=teacher.id))
    db.session.commit()
    return jsonify({"message": f"{teacher.name} now teaches {subject.name} in {section.full_name()}", "status": "success"})


# ---------------- Subjects (each class's syllabus)

def add_class_subject(class_id, name):
    school_class = SchoolClass.query.get(class_id)
    if not school_class:
        return jsonify({"message": "Class not found", "status": "failed"}), 404

    name = name.strip()
    if Subject.query.filter_by(class_id=class_id, name=name).first():
        return jsonify({"message": f"{school_class.name} already has {name}", "status": "failed"}), 409

    subject = Subject(name=name, class_id=class_id)
    db.session.add(subject)
    db.session.commit()
    return jsonify({"message": f"{name} added to {school_class.name}", "status": "success", "subject_id": subject.id}), 201


def rename_class_subject(subject_id, name):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found", "status": "failed"}), 404

    name = name.strip()
    other = Subject.query.filter_by(class_id=subject.class_id, name=name).first()
    if other and other.id != subject.id:
        return jsonify({"message": f"This class already has {name}", "status": "failed"}), 409

    subject.name = name
    db.session.commit()
    return jsonify({"message": "Subject updated", "status": "success"})


def remove_class_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found", "status": "failed"}), 404

    # Don't lose students' work: refuse while anything still uses the subject
    in_use = (Assignment.query.filter_by(subject_id=subject_id).count()
              + Result.query.filter_by(subject_id=subject_id).count()
              + Attendance.query.filter_by(subject_id=subject_id).count())
    if in_use > 0:
        return jsonify({"message": "This subject already has assignments, results or attendance, so it can't be deleted", "status": "failed"}), 409

    TeachingAssignment.query.filter_by(subject_id=subject_id).delete()
    SyllabusChapter.query.filter_by(subject_id=subject_id).delete()
    db.session.delete(subject)
    db.session.commit()
    return jsonify({"message": "Subject deleted", "status": "success"})


# ---------------- Syllabus chapters

def chapter_data(chapter):
    return {
        "id": chapter.id,
        "subject_id": chapter.subject_id,
        "number": chapter.number,
        "title": chapter.title,
        "description": chapter.description
    }


def get_subject_chapters(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found", "status": "failed"}), 404

    chapters = SyllabusChapter.query.filter_by(subject_id=subject_id).order_by(SyllabusChapter.number).all()
    chapter_list = []
    for chapter in chapters:
        chapter_list.append(chapter_data(chapter))

    return jsonify({
        "subject_id": subject.id,
        "subject_name": subject.name,
        "class_name": subject.school_class.name if subject.school_class else None,
        "data": chapter_list
    })


def add_subject_chapter(subject_id, title, description=None, number=None):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found", "status": "failed"}), 404

    # Without a number, the chapter goes at the end
    if number is None:
        last = SyllabusChapter.query.filter_by(subject_id=subject_id).order_by(SyllabusChapter.number.desc()).first()
        if last:
            number = last.number + 1
        else:
            number = 1

    if SyllabusChapter.query.filter_by(subject_id=subject_id, number=number).first():
        return jsonify({"message": f"Chapter {number} already exists", "status": "failed"}), 409

    chapter = SyllabusChapter(subject_id=subject_id, number=number, title=title.strip(), description=description)
    db.session.add(chapter)
    db.session.commit()
    return jsonify({"message": f"Chapter {number} added", "status": "success", "chapter": chapter_data(chapter)}), 201


def edit_subject_chapter(chapter_id, data):
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404

    if "number" in data and data["number"] != chapter.number:
        other = SyllabusChapter.query.filter_by(subject_id=chapter.subject_id, number=data["number"]).first()
        if other:
            return jsonify({"message": f"Chapter {data['number']} already exists", "status": "failed"}), 409
        chapter.number = data["number"]
    if "title" in data:
        chapter.title = data["title"].strip()
    if "description" in data:
        chapter.description = data["description"]

    db.session.commit()
    return jsonify({"message": "Chapter updated", "status": "success"})


def remove_subject_chapter(chapter_id):
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({"message": "Chapter deleted", "status": "success"})


# ---------------- Academic sessions

def session_data(session):
    return {
        "id": session.id,
        "name": session.name,
        "start_date": session.start_date.isoformat(),
        "end_date": session.end_date.isoformat(),
        "is_current": session.is_current
    }


def get_all_sessions():
    sessions = AcademicSession.query.order_by(AcademicSession.start_date.desc()).all()
    session_list = []
    for session in sessions:
        session_list.append(session_data(session))
    return jsonify(session_list)


def add_session(name, start_date, end_date, make_current=False):
    if end_date <= start_date:
        return jsonify({"message": "The session must end after it starts", "status": "failed"}), 400
    if AcademicSession.query.filter_by(name=name).first():
        return jsonify({"message": f"Session {name} already exists", "status": "failed"}), 409

    session = AcademicSession(name=name, start_date=start_date, end_date=end_date, is_current=False)
    db.session.add(session)
    db.session.commit()

    # The first session, or one asked to be current, becomes the current one
    if make_current or AcademicSession.query.count() == 1:
        set_current_session(session.id)

    return jsonify({"message": f"Session {name} added", "status": "success", "session_id": session.id}), 201


def set_current_session(session_id):
    session = AcademicSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found", "status": "failed"}), 404

    # Only one session is current at a time
    for other in AcademicSession.query.filter_by(is_current=True).all():
        other.is_current = False
    session.is_current = True
    db.session.commit()
    return jsonify({"message": f"{session.name} is now the current session", "status": "success"})


# ---------------- What a teacher or student sees

def get_teacher_classes(teacher_id):
    """The sections a teacher leads as class incharge, and the subjects they teach where."""
    incharge_list = []
    sections = Section.query.filter_by(teacher_id=teacher_id).all()
    for section in sections:
        incharge_list.append(section_summary(section))

    teaching_list = []
    teachings = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()
    for teaching in teachings:
        teaching_list.append({
            "section_id": teaching.section_id,
            "section_name": teaching.section.full_name(),
            "subject_id": teaching.subject_id,
            "subject_name": teaching.subject.name,
            "chapter_count": SyllabusChapter.query.filter_by(subject_id=teaching.subject_id).count(),
            "student_count": Student.query.filter_by(section_id=teaching.section_id).count()
        })

    return jsonify({
        "incharge_of": incharge_list,
        "teaching": teaching_list
    })


def get_student_class(student_id):
    """A student's own section and class, the class incharge, and who teaches each subject."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found", "status": "failed"}), 404

    section = student.section
    subject_list = []
    if section and section.class_id:
        subjects = Subject.query.filter_by(class_id=section.class_id).order_by(Subject.name).all()
        for subject in subjects:
            teaching = TeachingAssignment.query.filter_by(section_id=section.id, subject_id=subject.id).first()
            subject_list.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "teacher_name": teaching.teacher.name if teaching else None
            })

    return jsonify({
        "section_id": section.id if section else None,
        "section_name": section.full_name() if section else None,
        "class_name": section.school_class.name if section and section.school_class else None,
        "incharge_name": section.teacher.name if section and section.teacher else None,
        "roll_number": student.roll_number,
        "subjects": subject_list
    })
