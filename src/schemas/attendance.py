from marshmallow import Schema, fields, validate

class AttendanceSchema(Schema):
    student_id = fields.Int(required=True)
    subject_id = fields.Int(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["present", "absent", "late"]))

class UpdateAttendanceSchema(Schema):
    student_id = fields.Int(required=False)
    subject_id = fields.Int(required=False)
    date = fields.Date(required=False)
    time = fields.Time(required=False)
    status = fields.Str(validate=validate.OneOf(["present", "absent", "late"]),required=False)
