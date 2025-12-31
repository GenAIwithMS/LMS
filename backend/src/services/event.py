from src.models import Event
from src.db import db
from flask import jsonify

def add_event(title, description, event_date, event_time, admin_id):
    existing_event = Event.query.filter_by(title=title).first()
    if existing_event:
        return jsonify({
            "message":"Event title already exists try another",
            "status":"failed"
        }), 400
    
    new_event = Event(
        title=title,
        description=description,
        event_date=event_date,
        event_time=event_time,
        admin_id=admin_id
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({
        "message": "Event created successfully",
        "status": "success" 
    }), 201

def get_event_by_id(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({
            "message": "Event not found",
            "status": "error"
        }), 404

  
    result =  {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "event_date": str(event.event_date),
            "event_time": str(event.event_time),
            "admin_id": event.admin_id,
            "created_at": str(event.created_at)
        }
    return jsonify(result)

def get_all_events():
    events = Event.query.all()
    result = []
    for event in events:
        result.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "event_date": str(event.event_date),
            "event_time": str(event.event_time),
            "admin_id": event.admin_id,
            "created_at": str(event.created_at)
        })
    return jsonify(result)

def update_event(event_id, **kwargs):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({
            "message": "Event not found",
            "status": "error"
        }), 404

    for key, value in kwargs.items():
        if hasattr(event, key):
            setattr(event, key, value)
    db.session.commit()

    return jsonify({
        "message": "Event updated successfully",
        "status": "success"
    })

def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({
            "message": "Event not found",
            "status": "error"
        }), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({
        "message": "Event deleted successfully",
        "status": "success"
    })