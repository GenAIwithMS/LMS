from flask import jsonify
from src.db import db, pakistan_time
from src.models import ChapterProgress, Section, Subject, SyllabusChapter, TeachingAssignment


# Syllabus progress: each subject teacher marks how far their section has got with
# each chapter (not started, in progress, done). The school sees how much of the
# syllabus each section has covered.

PROGRESS_STATUSES = ["not_started", "in_progress", "done"]


def progress_percentage(done_count, chapter_count):
    if chapter_count == 0:
        return 0
    return round(done_count * 100 / chapter_count)


def get_subject_progress(section_id, subject_id):
    """Every chapter of the subject, with how far this section has got with it."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400

    chapters = SyllabusChapter.query.filter_by(subject_id=subject_id).order_by(SyllabusChapter.number).all()

    chapter_list = []
    done_count = 0
    for chapter in chapters:
        progress = ChapterProgress.query.filter_by(section_id=section_id, chapter_id=chapter.id).first()
        status = "not_started"
        planned_date = None
        started_on = None
        completed_on = None
        if progress:
            status = progress.status
            if progress.planned_date:
                planned_date = progress.planned_date.isoformat()
            if progress.started_on:
                started_on = progress.started_on.isoformat()
            if progress.completed_on:
                completed_on = progress.completed_on.isoformat()
        if status == "done":
            done_count = done_count + 1

        chapter_list.append({
            "chapter_id": chapter.id,
            "number": chapter.number,
            "title": chapter.title,
            "status": status,
            "planned_date": planned_date,
            "started_on": started_on,
            "completed_on": completed_on
        })

    teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject_id).first()

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "subject_id": subject.id,
        "subject_name": subject.name,
        "teacher_id": teaching.teacher_id if teaching else None,
        "teacher_name": teaching.teacher.name if teaching else None,
        "chapter_count": len(chapters),
        "done_count": done_count,
        "percentage": progress_percentage(done_count, len(chapters)),
        "chapters": chapter_list
    })


def get_section_progress(section_id):
    """For each subject of the section: chapters done, in progress, and the percentage covered."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject_list = []
    if section.class_id:
        subjects = Subject.query.filter_by(class_id=section.class_id).order_by(Subject.name).all()
        for subject in subjects:
            chapters = SyllabusChapter.query.filter_by(subject_id=subject.id).all()
            done_count = 0
            in_progress_count = 0
            for chapter in chapters:
                progress = ChapterProgress.query.filter_by(section_id=section_id, chapter_id=chapter.id).first()
                if progress and progress.status == "done":
                    done_count = done_count + 1
                if progress and progress.status == "in_progress":
                    in_progress_count = in_progress_count + 1

            teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject.id).first()
            subject_list.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "teacher_name": teaching.teacher.name if teaching else None,
                "chapter_count": len(chapters),
                "done_count": done_count,
                "in_progress_count": in_progress_count,
                "percentage": progress_percentage(done_count, len(chapters))
            })

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "subjects": subject_list
    })


def update_chapter_progress(section_id, chapter_id, data, teacher_id):
    """data can hold "status" and "planned_date". The start and finish dates fill in by themselves."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404

    progress = ChapterProgress.query.filter_by(section_id=section_id, chapter_id=chapter_id).first()
    if not progress:
        progress = ChapterProgress(section_id=section_id, chapter_id=chapter_id, status="not_started")
        db.session.add(progress)

    today = pakistan_time().date()

    if "status" in data:
        new_status = data["status"]
        if new_status not in PROGRESS_STATUSES:
            return jsonify({"message": f"Unknown status '{new_status}'", "status": "failed"}), 400

        if new_status == "not_started":
            progress.started_on = None
            progress.completed_on = None
        if new_status == "in_progress":
            if not progress.started_on:
                progress.started_on = today
            progress.completed_on = None
        if new_status == "done":
            if not progress.started_on:
                progress.started_on = today
            if not progress.completed_on:
                progress.completed_on = today
        progress.status = new_status

    if "planned_date" in data:
        progress.planned_date = data["planned_date"]

    progress.updated_by = teacher_id
    db.session.commit()

    return jsonify({"message": f"Chapter {chapter.number} updated", "status": "success"})
