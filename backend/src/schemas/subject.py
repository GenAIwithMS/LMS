from marshmallow import Schema, fields, validate

class subjectSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    # Send the IDs when you can: names can repeat, IDs can't
    teacher_id = fields.Integer(required=False)
    course_id = fields.Integer(required=False)
    teacher_name = fields.String(required=False, validate=validate.Length(min=2, max=100))
    course_name = fields.String(required=False, validate=validate.Length(min=2, max=100))

class UpdateSubjectSchema(Schema):
    teacher_id = fields.Integer(required=False)
    course_id = fields.Integer(required=False)
    name = fields.String(required=False, validate=validate.Length(min=2, max=100))
    teacher_name = fields.String(required=False, validate=validate.Length(min=2, max=100))
    course_name = fields.String(required=False, validate=validate.Length(min=2, max=100))
