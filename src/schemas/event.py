from marshmallow import Schema, fields, validate

class EventSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    event_date = fields.Date(required=True)
    event_time = fields.Time(required=False)
    admin_id = fields.Integer(dump_only=True)

class UpdateEventSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    event_date = fields.Date(required=False)
    event_time = fields.Time(required=False)
    admin_id = fields.Integer(required=False)