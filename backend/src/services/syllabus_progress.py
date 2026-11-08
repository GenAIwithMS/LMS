from flask import jsonify
from src.db import db, pakistan_time
from sqlalchemy.orm import selectinload
from src.models import ChapterProgress, Section, Subject, SyllabusChapter, TeachingAssignment, Assignment, ClassTest, DiaryEntry


# Syllabus progress: each section has its own syllabus (chapters with daily topics). The
# subject teacher ticks topics off, or marks a chapter without topics as not started, in
# progress or done. The school sees how much of the syllabus each section has covered.

PROGRESS_STATUSES = ["not_started", "in_progress", "done"]


def progress_percentage(done_count, chapter_count):
    if chapter_count == 0:
        return 0
    return round(done_count * 100 / chapter_count)


def topic_links(topic_ids):
    """{topic id: {"assignments": [...], "class_tests": [...], "diary": [...]}}, loaded in bulk."""
    links = {}
    for topic_id in topic_ids:
        links[topic_id] = {"assignments": [], "class_tests": [], "diary": []}
    if len(topic_ids) == 0:
        return links
    for assignment in Assignment.query.filter(Assignment.topic_id.in_(topic_ids)).all():
        links[assignment.topic_id]["assignments"].append({"id": assignment.id, "title": assignment.title,
                                                          "due_date": assignment.due_date.isoformat()})
    for test in ClassTest.query.filter(ClassTest.topic_id.in_(topic_ids)).all():
        links[test.topic_id]["class_tests"].append({"id": test.id, "title": test.title, "date": test.date.isoformat()})
    for entry in DiaryEntry.query.filter(DiaryEntry.topic_id.in_(topic_ids)).all():
        links[entry.topic_id]["diary"].append({"id": entry.id, "date": entry.date.isoformat()})
    return links


def get_subject_progress(section_id, subject_id, can_edit=False):
    """The section's syllabus for the subject: every chapter with its progress and daily topics,
    and what was made from each topic. can_edit: the person asking writes this syllabus."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400

    chapters = SyllabusChapter.query.options(selectinload(SyllabusChapter.topics)).filter_by(
        section_id=section_id, subject_id=subject_id).order_by(SyllabusChapter.number).all()

    progress_by_chapter = {}
    for progress in ChapterProgress.query.filter_by(section_id=section_id).all():
        progress_by_chapter[progress.chapter_id] = progress

    topic_ids = []
    for chapter in chapters:
        for topic in chapter.topics:
            topic_ids.append(topic.id)
    links = topic_links(topic_ids)

    chapter_list = []
    done_count = 0
    topic_count = 0
    topics_done = 0
    for chapter in chapters:
        progress = progress_by_chapter.get(chapter.id)
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

        topic_list = []
        for topic in chapter.topics:
            topic_count = topic_count + 1
            if topic.is_done:
                topics_done = topics_done + 1
            topic_list.append({
                "topic_id": topic.id,
                "number": topic.number,
                "title": topic.title,
                "planned_date": topic.planned_date.isoformat() if topic.planned_date else None,
                "is_done": topic.is_done,
                "done_on": topic.done_on.isoformat() if topic.done_on else None,
                "links": links[topic.id]
            })

        chapter_list.append({
            "chapter_id": chapter.id,
            "number": chapter.number,
            "title": chapter.title,
            "description": chapter.description,
            "status": status,
            "planned_date": planned_date,
            "started_on": started_on,
            "completed_on": completed_on,
            "topics": topic_list
        })

    teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject_id).first()

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "subject_id": subject.id,
        "subject_name": subject.name,
        "teacher_id": teaching.teacher_id if teaching else None,
        "teacher_name": teaching.teacher.name if teaching else None,
        "can_edit": can_edit,
        "chapter_count": len(chapters),
        "done_count": done_count,
        "percentage": progress_percentage(done_count, len(chapters)),
        "topic_count": topic_count,
        "topics_done": topics_done,
        "chapters": chapter_list
    })


def get_section_progress(section_id):
    """For each subject of the section: chapters done, in progress, and the percentage covered."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    subject_list = []
    if section.class_id:
        progress_by_chapter = {}
        for progress in ChapterProgress.query.filter_by(section_id=section_id).all():
            progress_by_chapter[progress.chapter_id] = progress
        all_chapters = SyllabusChapter.query.options(selectinload(SyllabusChapter.topics)).filter_by(section_id=section_id).all()

        subjects = Subject.query.filter_by(class_id=section.class_id).order_by(Subject.name).all()
        for subject in subjects:
            chapters = [chapter for chapter in all_chapters if chapter.subject_id == subject.id]
            done_count = 0
            in_progress_count = 0
            topic_count = 0
            topics_done = 0
            for chapter in chapters:
                progress = progress_by_chapter.get(chapter.id)
                if progress and progress.status == "done":
                    done_count = done_count + 1
                if progress and progress.status == "in_progress":
                    in_progress_count = in_progress_count + 1
                for topic in chapter.topics:
                    topic_count = topic_count + 1
                    if topic.is_done:
                        topics_done = topics_done + 1

            teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject.id).first()
            subject_list.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "teacher_id": teaching.teacher_id if teaching else None,
                "teacher_name": teaching.teacher.name if teaching else None,
                "chapter_count": len(chapters),
                "done_count": done_count,
                "in_progress_count": in_progress_count,
                "topic_count": topic_count,
                "topics_done": topics_done,
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
    if not chapter or (chapter.section_id is not None and chapter.section_id != section_id):
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404

    # A chapter with topics follows them (ticking topics off updates it)
    if "status" in data and len(chapter.topics) > 0:
        return jsonify({"message": "This chapter's progress follows its topics: tick the topics off instead", "status": "failed"}), 400

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
