from marshmallow import Schema, fields, validate


# ---------------- Terms and papers

class ExamTermSchema(Schema):
    session_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))   # like "First Term"
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    marks_deadline = fields.Date(required=False, allow_none=True)


class UpdateExamTermSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=2, max=50))
    start_date = fields.Date(required=False)
    end_date = fields.Date(required=False)
    marks_deadline = fields.Date(required=False, allow_none=True)
    is_locked = fields.Boolean(required=False)
    is_published = fields.Boolean(required=False)


class ClassPapersSchema(Schema):
    class_id = fields.Integer(required=True)
    total_marks = fields.Decimal(required=False, validate=validate.Range(min=1, max=999))
    passing_marks = fields.Decimal(required=False, validate=validate.Range(min=0, max=999))


class UpdatePaperSchema(Schema):
    total_marks = fields.Decimal(required=False, validate=validate.Range(min=1, max=999))
    passing_marks = fields.Decimal(required=False, validate=validate.Range(min=0, max=999))
    exam_date = fields.Date(required=False, allow_none=True)


class PaperReviewSchema(Schema):
    approve = fields.Boolean(required=True)
    note = fields.String(required=False, allow_none=True, validate=validate.Length(max=1000))


# ---------------- Marks, remarks and promotion

class PaperMarkRowSchema(Schema):
    student_id = fields.Integer(required=True)
    obtained_marks = fields.Decimal(required=False, allow_none=True, load_default=None)
    is_absent = fields.Boolean(required=False, load_default=False)


class PaperMarksSchema(Schema):
    marks = fields.List(fields.Nested(PaperMarkRowSchema), required=True)


class ReportRemarksSchema(Schema):
    remarks = fields.String(required=True, validate=validate.Length(max=1000))


class PromotionSchema(Schema):
    target_section_id = fields.Integer(required=True)
    student_ids = fields.List(fields.Integer(), required=True)
