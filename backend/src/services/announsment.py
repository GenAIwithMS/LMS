from src.models import Announcement, Section, SchoolClass
from flask import jsonify
from sqlalchemy.orm import joinedload
from src.db import db
  
def add_announcement(title, content, teacher_id, section_id,target_audience='all', created_at=None, from_incharge=False):
    existing_announcement = Announcement.query.filter_by(title=title).first()
    if existing_announcement:
        return jsonify({
            "message":"Announcement title already exists try another",
            "status":"failed"
        }), 400
    
    new_announcement = Announcement(
        title=title,
        content=content,
        target_audience=target_audience,
        section_id=section_id,
        teacher_id=teacher_id,
        from_incharge=from_incharge
    )
    if created_at:
        new_announcement.created_at = created_at

    db.session.add(new_announcement)
    db.session.commit()

    return jsonify({
        "message": "Announcement created successfully",
        "status": "success"
    }), 201

AUDIENCE_TEXT = {"all": "Everyone", "teachers": "Teachers", "students": "Students"}


def announcement_data(announcement):
    """One announcement for pages and the chatbot: who wrote it, who it's for, and where."""
    section = None
    if announcement.section_id:
        section = announcement.section

    # The author: a teacher or the admin
    author_role = "teacher"
    author_name = None
    if announcement.teacher:
        author_name = announcement.teacher.name
    if announcement.admin_id:
        author_role = "admin"
        if announcement.admin:
            author_name = announcement.admin.name

    # Where it goes: one section, one class, or the whole school
    where = "Whole school"
    class_name = None
    if announcement.school_class:
        class_name = announcement.school_class.name
        where = class_name + " (all sections)"
    if section:
        where = section.full_name()

    return {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "target_audience": announcement.target_audience,
        "audience_text": AUDIENCE_TEXT.get(announcement.target_audience, announcement.target_audience),
        "section_id": announcement.section_id,
        "section_name": section.full_name() if section else None,
        "class_id": announcement.class_id,
        "class_name": class_name,
        "where": where,
        "created_at": announcement.created_at,
        "teacher_id": announcement.teacher_id,
        "teacher_name": announcement.teacher.name if announcement.teacher else None,
        "admin_id": announcement.admin_id,
        "author_role": author_role,
        "author_name": author_name,
        # A class announcement from the section's class incharge
        "from_incharge": announcement.from_incharge,
        "author_text": author_text(announcement, author_role, author_name, section)
    }


def author_text(announcement, author_role, author_name, section):
    """Who posted it, for pages: "Principal (Admin)", "Sara Ahmed (Class incharge of Class 5 - A)" or "Omar Malik (Teacher)"."""
    name = author_name or "Unknown"
    if author_role == "admin":
        return name + " (Admin)"
    if announcement.from_incharge and section:
        return name + " (Class incharge of " + section.full_name() + ")"
    return name + " (Teacher)"


def get_all_announcements(allowed_ids=None, limit=None):
    """Announcements, newest first. allowed_ids: only these (what a student or teacher may see).
    limit: only the newest few (the notification bell).

    The author, section and class of every announcement are loaded in the same query,
    not one by one, so the list stays fast as announcements pile up over the year.
    """
    query = Announcement.query.options(
        joinedload(Announcement.teacher),
        joinedload(Announcement.admin),
        joinedload(Announcement.school_class),
        joinedload(Announcement.section).joinedload(Section.school_class),
    )
    if allowed_ids is not None:
        if len(allowed_ids) == 0:
            return jsonify([])
        query = query.filter(Announcement.id.in_(allowed_ids))
    query = query.order_by(Announcement.created_at.desc(), Announcement.id.desc())
    if limit:
        query = query.limit(limit)
    announcements = query.all()
    announcement_list = []
    for announcement in announcements:
        announcement_list.append(announcement_data(announcement))
    return jsonify(announcement_list)


def get_announcement_by_title(announcement_title):
    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement:
        return jsonify({
            "message": "Announcement not found",
            "status": "error"
        }), 404
    return jsonify(announcement_data(announcement))


def edit_announcement(announcement_title, **kwargs):
    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement:
        return jsonify({
            "message": "Announcement not found",
            "status": "error"
        }), 404

    # Announcements are found by title, so two must never share one
    new_title = kwargs.get('title')
    if new_title and new_title != announcement.title:
        other = Announcement.query.filter_by(title=new_title).first()
        if other:
            return jsonify({
                "message": "Announcement title already exists try another",
                "status": "failed"
            }), 400

    for key, value in kwargs.items():
        if hasattr(announcement, key):
            setattr(announcement, key, value)

    db.session.commit()

    return jsonify({
        "message": "Announcement updated successfully",
        "status": "success"
    })

def delete_announcement(announcement_title):
    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement:
        return jsonify({
            "message": "Announcement not found",
            "status": "error"
        }), 404

    db.session.delete(announcement)
    db.session.commit()

    return jsonify({
        "message": "Announcement deleted successfully",
        "status": "success"
    })

# ---------------- Announcements from the admin

def check_admin_target(class_id, section_id):
    """An error message if the class or section doesn't exist or don't match, otherwise None."""
    if class_id:
        if not SchoolClass.query.get(class_id):
            return "Class not found"
    if section_id:
        section = Section.query.get(section_id)
        if not section:
            return "Section not found"
        if class_id and section.class_id != class_id:
            return "This section is not in the chosen class"
    return None


def add_admin_announcement(admin_id, title, content, target_audience, class_id=None, section_id=None):
    title = title.strip()
    if Announcement.query.filter_by(title=title).first():
        return jsonify({"message": "Another announcement already has this title; choose another", "status": "failed"}), 400

    problem = check_admin_target(class_id, section_id)
    if problem:
        return jsonify({"message": problem, "status": "failed"}), 400

    # A section is enough on its own (it already belongs to a class)
    if section_id:
        class_id = None

    announcement = Announcement(title=title, content=content, target_audience=target_audience,
                                admin_id=admin_id, class_id=class_id, section_id=section_id)
    db.session.add(announcement)
    db.session.commit()
    return jsonify({"message": "Announcement posted", "status": "success", "announcement": announcement_data(announcement)}), 201


def edit_admin_announcement(announcement_id, data):
    """data can hold title, content, target_audience, class_id and section_id (None = whole school)."""
    announcement = Announcement.query.get(announcement_id)
    if not announcement or not announcement.admin_id:
        return jsonify({"message": "Announcement not found among the admin's announcements", "status": "failed"}), 404

    if "title" in data:
        new_title = data["title"].strip()
        other = Announcement.query.filter_by(title=new_title).first()
        if other and other.id != announcement.id:
            return jsonify({"message": "Another announcement already has this title; choose another", "status": "failed"}), 400

    # Where it goes: check the new class and section together
    class_id = announcement.class_id
    section_id = announcement.section_id
    if "class_id" in data or "section_id" in data:
        class_id = data.get("class_id")
        section_id = data.get("section_id")
        problem = check_admin_target(class_id, section_id)
        if problem:
            return jsonify({"message": problem, "status": "failed"}), 400
        if section_id:
            class_id = None

    if "title" in data:
        announcement.title = data["title"].strip()
    if "content" in data:
        announcement.content = data["content"]
    if "target_audience" in data:
        announcement.target_audience = data["target_audience"]
    announcement.class_id = class_id
    announcement.section_id = section_id
    db.session.commit()
    return jsonify({"message": "Announcement updated", "status": "success", "announcement": announcement_data(announcement)})


def delete_announcement_by_id(announcement_id):
    """The admin can remove any announcement, a teacher's too."""
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({"message": "Announcement not found", "status": "failed"}), 404
    db.session.delete(announcement)
    db.session.commit()
    return jsonify({"message": "Announcement deleted", "status": "success"})
