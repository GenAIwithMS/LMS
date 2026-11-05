from src.models import Event
from src.db import db, pakistan_time
from flask import jsonify

def time_text(event_time):
    """The time like "09:00", or None when there is no time."""
    if event_time is None:
        return None
    return event_time.strftime("%H:%M")


def add_event(title, description, event_date, event_time, admin_id):
    existing_event = Event.query.filter_by(title=title).first()
    if existing_event:
        return jsonify({
            "message":"Event title already exists try another",
            "status":"failed"
        }), 400

    # An event is something coming up, so it can't be in the past
    if event_date < pakistan_time().date():
        return jsonify({
            "message": "The event date is in the past; choose today or a later date",
            "status": "failed"
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
            "event_time": time_text(event.event_time),
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
            "event_time": time_text(event.event_time),
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

    # A new date can't be in the past (an event that has already happened can keep its date)
    new_date = kwargs.get("event_date")
    if new_date is not None and new_date != event.event_date and new_date < pakistan_time().date():
        return jsonify({
            "message": "The event date is in the past; choose today or a later date",
            "status": "failed"
        }), 400

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