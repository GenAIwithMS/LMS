from marshmallow import Schema, fields, validate

class AttendanceSchema(Schema):
    # Send student_id when you can: names are not unique, IDs are
    student_id = fields.Int(required=False)
    student_name = fields.Str(required=False)
    subject_name = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["present", "absent", "late"]))

class UpdateAttendanceSchema(Schema):
    student_id = fields.Int(required=False)
    student_name = fields.Str(required=False)
    subject_name = fields.Str(required=False)
    status = fields.Str(validate=validate.OneOf(["present", "absent", "late"]),required=False)
