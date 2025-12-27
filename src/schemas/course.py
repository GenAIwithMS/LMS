from marshmallow import Schema, fields, validate

class CourseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    course_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    teacher_name = fields.String(required=True)
    created_at = fields.DateTime(required=False)

class UpdateCourseSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    course_code = fields.String(required=False, validate=validate.Length(min=1, max=50))
    teacher_name = fields.String(required=False)