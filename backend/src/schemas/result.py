from marshmallow import Schema, fields, validate

class ResultSchema(Schema):

    id = fields.Integer(dump_only=True)
    # Send student_id when you can: names are not unique, IDs are
    student_id = fields.Integer(required=False)
    student_name = fields.String(required=False)
    subject_id = fields.Integer(required=False)   # preferred: names can repeat
    subject_name = fields.String(required=False)
    total_marks = fields.Decimal(as_string=True, required=True)
    exam_type = fields.String(required=True, validate=validate.OneOf(['midterm', 'final', 'quiz', 'assignment']))
    remarks = fields.String(required=False, validate=validate.Length(max=255))
    obtained_marks = fields.Decimal(as_string=True, required=True)

class UpdateResultSchema(Schema):
    subject_id = fields.Integer(required=False)
    student_id = fields.Integer(required=False)
    student_name = fields.String(required=False)
    subject_name = fields.String(required=False)
    total_marks = fields.Decimal(as_string=True, required=False)
    exam_type = fields.String(required=False, validate=validate.OneOf(['midterm', 'final', 'quiz', 'assignment']))
    remarks = fields.String(required=False, validate=validate.Length(max=255))
    obtained_marks = fields.Decimal(as_string=True, required=False)