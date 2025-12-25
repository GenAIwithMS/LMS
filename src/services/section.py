from src.models.section import Section
from flask import jsonify
from src.db import db

def add_section(name, teacher_id):
    #check if section name already exists
    existing_section = Section.query.filter_by(name=name).first()
    if existing_section:
        return jsonify({
            "message":"Section name already exists try another",
            "status":"failed"
        }), 400
    
    new_section = Section(
        name=name,
        teacher_id=teacher_id
    )
    db.session.add(new_section)
    db.session.commit()

    return jsonify({
        "message":"section added successfully",
        "status":"success"
    })

def get_section_by_id(section_id):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({
            "message":"section not found",
            "status":"error"
        }), 400

    return jsonify({
        "id": section.id,
        "name": section.name,
        "teacher_id": section.teacher_id
    })

def get_all_sections():
    sections = Section.query.all()
    section_list = []
    for section in sections:
        section_list.append({
            "id": section.id,
            "name": section.name,
            "teacher_id": section.teacher_id
        })
    return jsonify(section_list)

def edit_section(section_id, **kwargs):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({
            "message":"section not found",
            "status":"error"
        }), 400
    
    for key, value in kwargs.items():
        if hasattr(section, key):
            setattr(section, key, value)

    db.session.commit()

    return jsonify({
        "message":"section updated successfully",
        "status":"success"
    })

def delete_section(section_id):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({
            "message":"section not found",
            "status":"error"
        }), 400

    db.session.delete(section)
    db.session.commit()

    return jsonify({
        "message":"section deleted successfully",
        "status":"success"
    })