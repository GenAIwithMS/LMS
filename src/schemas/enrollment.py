from marshmallow import Schema, fields, validate
from src.db import db


class EnrollmentSchema(Schema):
    id = fields.Integer(dump_only=True)
    student_id = fields.Integer(required=True)
    course_id = fields.Integer(required=True)
    enrollment_date = fields.Date(required=True)
    status = fields.String(validate=validate.OneOf(['active', 'completed', 'dropped']))
    grade = fields.String(required=False)

class UpdateEnrollmentSchema(Schema):
    student_id = fields.Integer(required=False)
    course_id = fields.Integer(required=False)
    enrollment_date = fields.Date(required=False)
    status = fields.String(validate=validate.OneOf(['active', 'completed', 'dropped']),required=False)
    grade = fields.String(required=False)
    
