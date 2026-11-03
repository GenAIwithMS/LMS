from marshmallow import Schema, fields, validate

class AnnouncementSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content = fields.String(required=True)
    target_audience = fields.String()
    section_id = fields.Integer(required=False)   # preferred: names can repeat
    section_name = fields.String(required=False)
    teacher_id = fields.Integer(dump_only=True)

class UpdateAnnouncementSchema(Schema):
    section_id = fields.Integer(required=False)
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    content = fields.String(required=False)
    target_audience = fields.String(required=False)
    section_name = fields.String(required=False)
    teacher_id = fields.Integer(dump_only=True)