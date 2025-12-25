from marshmallow import Schema, fields, validate

class AnnouncementSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content = fields.String(required=True)
    target_audience = fields.String()
    section_id = fields.Integer(required=True)
    teacher_id = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)

class UpdateAnnouncementSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    content = fields.String(required=False)
    target_audience = fields.String(required=False)
    section_id = fields.Integer(required=False)
    teacher_id = fields.Integer(required=False)