from marshmallow import Schema, fields, validate

class ResultSchema(Schema):

    id = fields.Integer(dump_only=True)
    student_id = fields.Integer(required=True)
    subject_id = fields.Integer(required=True)
    total_marks = fields.Decimal(as_string=True, required=True)
    exam_type = fields.String(required=True, validate=validate.Length(min=2, max=50))
    remarks = fields.String(required=False, validate=validate.Length(max=255))
    marks_obtained = fields.Decimal(as_string=True, required=True)