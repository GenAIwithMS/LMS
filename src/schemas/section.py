from marshmallow import Schema, fields

class SectionSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    teacher_id = fields.Integer(required=True)


class UpdateSectionSchema(Schema):
    name = fields.String(required=False)
    teacher_id = fields.Integer(required=False)