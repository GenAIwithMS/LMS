from src.models.course import Course
from marshmallow import Schema, fields, validate

class CourseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False)
    course_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    teacher_id = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)