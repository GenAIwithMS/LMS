from marshmallow import Schema, fields

class SectionSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    teacher_name = fields.String(required=True)


class UpdateSectionSchema(Schema):
    name = fields.String(required=False)
    teacher_name = fields.String(required=False)