from marshmallow import Schema, fields, validate

class subjectSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    teacher_id = fields.Integer(required=True)
    course_code = fields.String(required=True, validate=validate.Length(min=2, max=20))

class UpdateSubjectSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=2, max=100))
    teacher_id = fields.Integer(required=False)
    course_code = fields.String(required=False, validate=validate.Length(min=2, max=20))
