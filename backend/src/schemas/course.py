from marshmallow import Schema, fields, validate

class CourseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    course_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    teacher_id = fields.Integer(required=False)   # preferred: names can repeat
    teacher_name = fields.String(required=False)
    created_at = fields.DateTime(required=False)

class UpdateCourseSchema(Schema):
    teacher_id = fields.Integer(required=False)
    name = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    course_code = fields.String(required=False, validate=validate.Length(min=1, max=50))
    created_at = fields.DateTime(required=False)
    teacher_name = fields.String(required=False)