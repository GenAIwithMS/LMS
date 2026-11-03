from marshmallow import Schema, fields

class SectionSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    teacher_id = fields.Integer(required=False)   # preferred: names can repeat
    teacher_name = fields.String(required=False)


class UpdateSectionSchema(Schema):
    teacher_id = fields.Integer(required=False)
    name = fields.String(required=False)
    teacher_name = fields.String(required=False)