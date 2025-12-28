from marshmallow import Schema, fields, validate

class ResultSchema(Schema):

    id = fields.Integer(dump_only=True)
    student_name = fields.String(required=True)
    subject_name = fields.String(required=True)
    total_marks = fields.Decimal(as_string=True, required=True)
    exam_type = fields.String(required=True, validate=validate.Length(min=2, max=50))
    remarks = fields.String(required=False, validate=validate.Length(max=255))
    obtained_marks = fields.Decimal(as_string=True, required=True)

class UpdateResultSchema(Schema):
    student_name = fields.String(required=False)
    subject_name = fields.String(required=False)
    total_marks = fields.Decimal(as_string=True, required=False)
    exam_type = fields.String(required=False, validate=validate.Length(min=2, max=50))
    remarks = fields.String(required=False, validate=validate.Length(max=255))
    obtained_marks = fields.Decimal(as_string=True, required=False)