from marshmallow import Schema, fields, validate

class assignmentSchema(Schema):
    
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    subject_name = fields.String(required=True)
    teacher_name = fields.String(dump_only=True)
    due_date = fields.Date(required=True)
    description = fields.String(required=True)
    total_marks = fields.Decimal(as_string=True)

class UpdateAssignmentSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    subject_name = fields.String(required=False)
    teacher_name = fields.String(dump_only=True)
    due_date = fields.Date(required=False)
    description = fields.String(required=False)
    total_marks = fields.Decimal(as_string=True, required=False)