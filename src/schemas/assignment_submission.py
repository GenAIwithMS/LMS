from marshmallow import Schema, fields, validate

class AssignmentSubmissionSchema(Schema):
   
    id = fields.Integer(dump_only=True)
    assignment_id = fields.Integer(required=True)
    student_id = fields.Integer(dump_only=True)
    submission_file = fields.Raw(required=False)
    submission_text = fields.String(required=False)
    submitted_at = fields.DateTime(required=False)
    feedback = fields.String(required=False)

class UpdateAssignmentSubmissionSchema(Schema):
    assignment_id = fields.Integer(required=False)
    student_id = fields.Integer(dump_only=True)
    submission_file = fields.Raw(required=False)
    submission_text = fields.String(required=False)
    submitted_at = fields.DateTime(required=False)
    feedback = fields.String(required=False)
