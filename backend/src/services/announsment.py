from src.models import Announcement,Section
from flask import jsonify
from src.db import db
  
def add_announcement(title, content, teacher_id, section_id,target_audience='all', created_at=None):
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
        teacher_id=teacher_id
    )
    if created_at:
        new_announcement.created_at = created_at

    db.session.add(new_announcement)
    db.session.commit()

    return jsonify({
        "message": "Announcement created successfully",
        "status": "success"
    }), 201

def get_all_announcements():
    
    announcements = Announcement.query.all()

    announcement_list = []
    for announcement in announcements:
        section = Section.query.get(announcement.section_id)
        announcement_data = {
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "target_audience": announcement.target_audience,
            "section_id": announcement.section_id,
            "section_name": section.name if section else None,
            "created_at": announcement.created_at,
            "teacher_id": announcement.teacher_id,
            "teacher_name": announcement.teacher.name if announcement.teacher else None
        }
        announcement_list.append(announcement_data)
    return jsonify(announcement_list)

def get_announcement_by_title(announcement_title):
    announcement = Announcement.query.filter_by(title=announcement_title).first()
    if not announcement:
        return jsonify({
            "message": "Announcement not found",
            "status": "error"
        }), 404

    section = Section.query.get(announcement.section_id)
    announcement_data = {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "target_audience": announcement.target_audience,
        "section_id": announcement.section_id,
        "section_name": section.name if section else None,
        "created_at": announcement.created_at,
        "teacher_id": announcement.teacher_id,
        "teacher_name": announcement.teacher.name if announcement.teacher else None
    }
    return jsonify(announcement_data)

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