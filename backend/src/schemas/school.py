from marshmallow import Schema, fields, validate


class ClassSectionSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    incharge_id = fields.Integer(required=False, allow_none=True)


class UpdateClassSectionSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=50))
    incharge_id = fields.Integer(required=False, allow_none=True)   # null removes the incharge


class SubjectTeacherSchema(Schema):
    subject_id = fields.Integer(required=True)
    teacher_id = fields.Integer(required=True, allow_none=True)     # null removes the teacher


class ClassSubjectSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))


class ChapterSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, allow_none=True)
    number = fields.Integer(required=False, validate=validate.Range(min=1))


class UpdateChapterSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, allow_none=True)
    number = fields.Integer(required=False, validate=validate.Range(min=1))


class AcademicSessionSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=4, max=20))   # like "2026-27"
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    is_current = fields.Boolean(required=False)


class TeacherSubjectSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))   # like "Urdu"
