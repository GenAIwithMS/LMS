from marshmallow import Schema, fields, validate


class EnrollmentSchema(Schema):
    id = fields.Integer(dump_only=True)
    student_name = fields.String(required=True)
    course_name = fields.String(required=True)
    enrollment_date = fields.Date(required=False)
    status = fields.String(validate=validate.OneOf(['active', 'completed', 'dropped']))
    grade = fields.String(required=False)

class UpdateEnrollmentSchema(Schema):
    student_name = fields.String(required=False)
    course_name = fields.String(required=False)
    enrollment_date = fields.Date(required=False)
    status = fields.String(validate=validate.OneOf(['active', 'completed', 'dropped']),required=False)
    grade = fields.String(required=False)
    
