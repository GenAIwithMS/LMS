from marshmallow import Schema, fields, post_load

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
    marks = fields.Decimal(as_string=True, required=False, allow_none=True)
    marks_obtained = fields.Decimal(as_string=True, required=False, allow_none=True, load_only=True)
    feedback = fields.String(required=False)
    
    @post_load
    def process_marks(self, data, **kwargs):
        if 'marks_obtained' in data:
            if 'marks' not in data or data.get('marks') is None:
                data['marks'] = data.pop('marks_obtained')
            else:
                data.pop('marks_obtained', None)
        return data
