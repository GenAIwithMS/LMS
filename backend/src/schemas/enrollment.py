from marshmallow import Schema, fields, validate


class EnrollmentSchema(Schema):
    id = fields.Integer(dump_only=True)
    # Send student_id when you can: names are not unique, IDs are
    student_id = fields.Integer(required=False)
    student_name = fields.String(required=False)
    course_name = fields.String(required=True)
    enrollment_date = fields.Date(required=False)
    status = fields.String(validate=validate.OneOf(['active', 'completed', 'dropped']))
    grade = fields.String(required=False)

class UpdateEnrollmentSchema(Schema):
    student_id = fields.Integer(required=False)
    student_name = fields.String(required=False)
    course_name = fields.String(required=False)
    enrollment_date = fields.Date(required=False)
    status = fields.String(validate=validate.OneOf(['active', 'completed', 'dropped']),required=False)
    grade = fields.String(required=False)
    
