from src.schemas.event import EventSchema,UpdateEventSchema
from src.services.event import add_event, get_event_by_id, get_all_events,update_event,delete_event
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity


event_bp = Blueprint("event", __name__)

@event_bp.route("/api/create/event", methods=["POST"])
@jwt_required()
def create_ev():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can create events",
            "staus":"failed"
        }),403

    try:
        data = EventSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    admin_id = int(get_jwt_identity())
    title = data.get("title")
    description = data.get("description")
    event_date = data.get("event_date")
    event_time = data.get("event_time")

    result = add_event(
        title=title,
        description=description,
        event_date=event_date,
        event_time=event_time,
        admin_id=admin_id
    )
    return result

@event_bp.route("/api/get/events", methods=["GET"])
@jwt_required()
def get_events():
    event_id = request.args.get("id", type=int)
    if event_id:
        result = get_event_by_id(event_id)
    else:
        result = get_all_events()
    return result

@event_bp.route("/api/update/event", methods=["PUT"])
@jwt_required()
def update_ev():
     
    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can update events",
            "staus":"failed"
        }),403
    
    event_id = request.args.get("id", type=int)
    if not event_id:
        return jsonify({
            "message": "Event ID is required",
            "status": "error"
        }), 400
    try:
        data = UpdateEventSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    result = update_event(event_id, **data)
    return result

@event_bp.route("/api/delete/event", methods=["DELETE"])
@jwt_required()
def delete_ev():

    token = get_jwt()
    if token["role"] != "admin":
        return jsonify({
            "message":"only admins can create events",
            "staus":"failed"
        }),403
     
    event_id = request.args.get("id", type=int)
    if not event_id:
        return jsonify({
            "message": "Event ID is required",
            "status": "error"
        }), 400

    result = delete_event(event_id)
    return result