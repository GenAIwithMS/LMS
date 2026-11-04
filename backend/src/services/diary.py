from flask import jsonify
from src.db import db
from src.models import DiaryEntry, Section, Subject


# The daily diary: for each subject, what was taught today (classwork) and the homework.
# One entry per section, subject and day. Students see their own section's diary.


def diary_data(entry):
    return {
        "id": entry.id,
        "section_id": entry.section_id,
        "section_name": entry.section.full_name(),
        "subject_id": entry.subject_id,
        "subject_name": entry.subject.name,
        "teacher_id": entry.teacher_id,
        "teacher_name": entry.teacher.name,
        "date": entry.date.isoformat(),
        "classwork": entry.classwork,
        "homework": entry.homework
    }


def get_section_diary(section_id, day):
    """All of a section's diary entries for one day, by subject."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    entries = DiaryEntry.query.filter_by(section_id=section_id, date=day).all()

    entry_list = []
    for entry in entries:
        entry_list.append(diary_data(entry))
    entry_list.sort(key=lambda item: item["subject_name"])

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "date": day.isoformat(),
        "entries": entry_list
    })


def save_diary_entry(section_id, subject_id, day, classwork, homework, teacher_id):
    """Write the diary for a subject on a day. Writing the same day again updates it."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400

    if not classwork and not homework:
        return jsonify({"message": "Write the classwork, the homework, or both", "status": "failed"}), 400

    entry = DiaryEntry.query.filter_by(section_id=section_id, subject_id=subject_id, date=day).first()
    if entry:
        entry.classwork = classwork
        entry.homework = homework
        entry.teacher_id = teacher_id
        message = "Diary updated"
        status_code = 200
    else:
        entry = DiaryEntry(
            section_id=section_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            date=day,
            classwork=classwork,
            homework=homework
        )
        db.session.add(entry)
        message = "Diary saved"
        status_code = 201
    db.session.commit()

    return jsonify({"message": message, "status": "success", "entry": diary_data(entry)}), status_code


def delete_diary_entry(entry_id):
    entry = DiaryEntry.query.get(entry_id)
    if not entry:
        return jsonify({"message": "Diary entry not found", "status": "failed"}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Diary entry deleted", "status": "success"})
