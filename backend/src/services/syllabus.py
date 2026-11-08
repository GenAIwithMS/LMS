from flask import jsonify
from src.db import db, pakistan_time
from src.models import (SyllabusChapter, SyllabusTopic, ChapterProgress, ClassTest, Assignment, DiaryEntry,
                        Section, Subject, TeachingAssignment)


# The syllabus of one subject in one section: chapters, each with daily topics.
#
# The teacher who teaches the subject in the section writes it (adds, renames, reorders and
# deletes chapters and topics) and ticks topics off as they are taught. The admin and the
# section's students can only see it. When a chapter has topics, its progress follows them:
# some done = in progress, all done = done.


def check_section_subject(section_id, subject_id):
    """(section, subject, error answer). The subject must belong to the section's class."""
    section = Section.query.get(section_id)
    if not section:
        return None, None, (jsonify({"message": "Section not found", "status": "failed"}), 404)
    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return None, None, (jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400)
    return section, subject, None


def teacher_can_edit(teacher_id, section_id, subject_id):
    """True if this teacher teaches the subject in the section (so they write its syllabus)."""
    teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject_id, teacher_id=teacher_id).first()
    return teaching is not None


def chapter_data(chapter):
    return {
        "id": chapter.id,
        "subject_id": chapter.subject_id,
        "section_id": chapter.section_id,
        "number": chapter.number,
        "title": chapter.title,
        "description": chapter.description
    }


def get_section_subject_chapters(section_id, subject_id):
    """The chapters of a subject in a section (for pickers, e.g. a class test's chapter)."""
    section, subject, error = check_section_subject(section_id, subject_id)
    if error:
        return error
    chapters = SyllabusChapter.query.filter_by(section_id=section_id, subject_id=subject_id).order_by(SyllabusChapter.number).all()
    chapter_list = []
    for chapter in chapters:
        data = chapter_data(chapter)
        topic_list = []
        for topic in chapter.topics:
            topic_list.append({"id": topic.id, "number": topic.number, "title": topic.title, "is_done": topic.is_done})
        data["topics"] = topic_list
        chapter_list.append(data)
    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "subject_id": subject.id,
        "subject_name": subject.name,
        "data": chapter_list
    })


# ---------------- Chapters

def next_number(numbers):
    """The number after the largest one (1 for an empty list)."""
    if len(numbers) == 0:
        return 1
    return max(numbers) + 1


def add_chapter(section_id, subject_id, title, description=None):
    section, subject, error = check_section_subject(section_id, subject_id)
    if error:
        return error
    numbers = [c.number for c in SyllabusChapter.query.filter_by(section_id=section_id, subject_id=subject_id).all()]
    chapter = SyllabusChapter(subject_id=subject_id, section_id=section_id, number=next_number(numbers),
                              title=title.strip(), description=description)
    db.session.add(chapter)
    db.session.commit()
    return jsonify({"message": f"Chapter {chapter.number} added", "status": "success", "chapter": chapter_data(chapter)}), 201


def edit_chapter(chapter_id, data):
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404
    if "title" in data:
        chapter.title = data["title"].strip()
    if "description" in data:
        chapter.description = data["description"]
    db.session.commit()
    return jsonify({"message": "Chapter updated", "status": "success", "chapter": chapter_data(chapter)})


def remove_chapter(chapter_id):
    """Delete a chapter with its topics and progress. Tests, assignments and diary entries
    made from it stay, without the chapter or topic."""
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404

    for topic in chapter.topics:
        unlink_topic(topic.id)
        db.session.delete(topic)
    ChapterProgress.query.filter_by(chapter_id=chapter_id).delete(synchronize_session=False)
    for test in ClassTest.query.filter_by(chapter_id=chapter_id).all():
        test.chapter_id = None
    section_id = chapter.section_id
    subject_id = chapter.subject_id
    number = chapter.number
    db.session.delete(chapter)
    db.session.flush()

    # Close the gap: the chapters after it move up one
    later = SyllabusChapter.query.filter(SyllabusChapter.section_id == section_id, SyllabusChapter.subject_id == subject_id,
                                         SyllabusChapter.number > number).order_by(SyllabusChapter.number).all()
    for other in later:
        other.number = other.number - 1
        db.session.flush()
    db.session.commit()
    return jsonify({"message": "Chapter deleted", "status": "success"})


def swap_numbers(first, second):
    """Swap the numbers of two rows without ever having two with the same number."""
    first_number = first.number
    second_number = second.number
    first.number = -first_number
    db.session.flush()
    second.number = first_number
    db.session.flush()
    first.number = second_number
    db.session.flush()


def move_chapter(chapter_id, direction):
    """direction "up" or "down": swap the chapter with the one before or after it."""
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404
    query = SyllabusChapter.query.filter_by(section_id=chapter.section_id, subject_id=chapter.subject_id)
    if direction == "up":
        neighbour = query.filter(SyllabusChapter.number < chapter.number).order_by(SyllabusChapter.number.desc()).first()
    else:
        neighbour = query.filter(SyllabusChapter.number > chapter.number).order_by(SyllabusChapter.number).first()
    if not neighbour:
        return jsonify({"message": "The chapter is already at the " + ("top" if direction == "up" else "bottom"), "status": "failed"}), 400
    swap_numbers(chapter, neighbour)
    db.session.commit()
    return jsonify({"message": "Chapter moved", "status": "success"})


# ---------------- Topics

def topic_data(topic):
    return {
        "id": topic.id,
        "chapter_id": topic.chapter_id,
        "number": topic.number,
        "title": topic.title,
        "planned_date": topic.planned_date.isoformat() if topic.planned_date else None,
        "is_done": topic.is_done,
        "done_on": topic.done_on.isoformat() if topic.done_on else None
    }


def add_topic(chapter_id, title, planned_date=None):
    chapter = SyllabusChapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found", "status": "failed"}), 404
    numbers = [t.number for t in chapter.topics]
    topic = SyllabusTopic(chapter_id=chapter_id, number=next_number(numbers), title=title.strip(), planned_date=planned_date)
    db.session.add(topic)
    db.session.flush()
    # A new topic that isn't done yet means the chapter isn't finished any more
    refresh_chapter_progress(chapter, None)
    db.session.commit()
    return jsonify({"message": "Topic added", "status": "success", "topic": topic_data(topic)}), 201


def edit_topic(topic_id, data):
    topic = SyllabusTopic.query.get(topic_id)
    if not topic:
        return jsonify({"message": "Topic not found", "status": "failed"}), 404
    if "title" in data:
        topic.title = data["title"].strip()
    if "planned_date" in data:
        topic.planned_date = data["planned_date"]
    db.session.commit()
    return jsonify({"message": "Topic updated", "status": "success", "topic": topic_data(topic)})


def unlink_topic(topic_id):
    """Assignments, tests and diary entries made from the topic keep existing, without it."""
    Assignment.query.filter_by(topic_id=topic_id).update({"topic_id": None}, synchronize_session=False)
    ClassTest.query.filter_by(topic_id=topic_id).update({"topic_id": None}, synchronize_session=False)
    DiaryEntry.query.filter_by(topic_id=topic_id).update({"topic_id": None}, synchronize_session=False)


def remove_topic(topic_id, teacher_id):
    topic = SyllabusTopic.query.get(topic_id)
    if not topic:
        return jsonify({"message": "Topic not found", "status": "failed"}), 404
    chapter = topic.chapter
    number = topic.number
    unlink_topic(topic_id)
    db.session.delete(topic)
    db.session.flush()
    later = SyllabusTopic.query.filter(SyllabusTopic.chapter_id == chapter.id, SyllabusTopic.number > number).order_by(SyllabusTopic.number).all()
    for other in later:
        other.number = other.number - 1
        db.session.flush()
    db.session.expire(chapter, ["topics"])
    refresh_chapter_progress(chapter, teacher_id)
    db.session.commit()
    return jsonify({"message": "Topic deleted", "status": "success"})


def move_topic(topic_id, direction):
    topic = SyllabusTopic.query.get(topic_id)
    if not topic:
        return jsonify({"message": "Topic not found", "status": "failed"}), 404
    query = SyllabusTopic.query.filter_by(chapter_id=topic.chapter_id)
    if direction == "up":
        neighbour = query.filter(SyllabusTopic.number < topic.number).order_by(SyllabusTopic.number.desc()).first()
    else:
        neighbour = query.filter(SyllabusTopic.number > topic.number).order_by(SyllabusTopic.number).first()
    if not neighbour:
        return jsonify({"message": "The topic is already at the " + ("top" if direction == "up" else "bottom"), "status": "failed"}), 400
    swap_numbers(topic, neighbour)
    db.session.commit()
    return jsonify({"message": "Topic moved", "status": "success"})


def set_topic_done(topic_id, done, teacher_id):
    """Tick a topic off (done=True) or back (done=False). The chapter's progress follows."""
    topic = SyllabusTopic.query.get(topic_id)
    if not topic:
        return jsonify({"message": "Topic not found", "status": "failed"}), 404
    topic.is_done = done
    if done:
        topic.done_on = pakistan_time().date()
    else:
        topic.done_on = None
    db.session.flush()
    refresh_chapter_progress(topic.chapter, teacher_id)
    db.session.commit()
    if done:
        message = f"Topic {topic.number} done"
    else:
        message = f"Topic {topic.number} marked as not done"
    return jsonify({"message": message, "status": "success", "topic": topic_data(topic)})


def refresh_chapter_progress(chapter, teacher_id):
    """A chapter with topics: none done = not started, some = in progress, all = done."""
    topics = SyllabusTopic.query.filter_by(chapter_id=chapter.id).all()
    if len(topics) == 0 or chapter.section_id is None:
        return
    done_count = 0
    for topic in topics:
        if topic.is_done:
            done_count = done_count + 1

    if done_count == 0:
        status = "not_started"
    elif done_count == len(topics):
        status = "done"
    else:
        status = "in_progress"

    progress = ChapterProgress.query.filter_by(section_id=chapter.section_id, chapter_id=chapter.id).first()
    if not progress:
        progress = ChapterProgress(section_id=chapter.section_id, chapter_id=chapter.id, status="not_started")
        db.session.add(progress)

    today = pakistan_time().date()
    if status == "not_started":
        progress.started_on = None
        progress.completed_on = None
    if status == "in_progress":
        if not progress.started_on:
            progress.started_on = today
        progress.completed_on = None
    if status == "done":
        if not progress.started_on:
            progress.started_on = today
        progress.completed_on = today
    progress.status = status
    if teacher_id:
        progress.updated_by = teacher_id


def find_topic_for(topic_id, section_id, subject_id):
    """The topic, if it belongs to this section's subject (to link a new assignment, test or
    diary entry to it). (topic, error message)"""
    if not topic_id:
        return None, None
    topic = SyllabusTopic.query.get(topic_id)
    if not topic or topic.chapter.section_id != section_id or topic.chapter.subject_id != subject_id:
        return None, "This topic is not part of this class's subject"
    return topic, None
