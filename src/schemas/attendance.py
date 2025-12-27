from marshmallow import Schema, fields, validate

class AttendanceSchema(Schema):
    student_name = fields.Str(required=True)
    subject_name = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["present", "absent", "late"]))

class UpdateAttendanceSchema(Schema):
    student_name = fields.Str(required=False)
    subject_name = fields.Str(required=False)
    status = fields.Str(validate=validate.OneOf(["present", "absent", "late"]),required=False)
