from marshmallow import Schema, fields, validate


# ---------------- Daily attendance

class AttendanceRowSchema(Schema):
    student_id = fields.Integer(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["present", "absent", "late", "leave"]))


class DailyAttendanceSchema(Schema):
    date = fields.Date(required=True)
    records = fields.List(fields.Nested(AttendanceRowSchema), required=True)


# ---------------- Syllabus progress

class ChapterProgressSchema(Schema):
    status = fields.String(required=False, validate=validate.OneOf(["not_started", "in_progress", "done"]))
    planned_date = fields.Date(required=False, allow_none=True)


# ---------------- Diary

class DiaryEntrySchema(Schema):
    subject_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    classwork = fields.String(required=False, allow_none=True, validate=validate.Length(max=5000))
    homework = fields.String(required=False, allow_none=True, validate=validate.Length(max=5000))


# ---------------- Class tests

class ClassTestSchema(Schema):
    section_id = fields.Integer(required=True)
    subject_id = fields.Integer(required=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    date = fields.Date(required=True)
    total_marks = fields.Decimal(required=True, validate=validate.Range(min=1, max=999))
    chapter_id = fields.Integer(required=False, allow_none=True)


class UpdateClassTestSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    date = fields.Date(required=False)
    total_marks = fields.Decimal(required=False, validate=validate.Range(min=1, max=999))
    chapter_id = fields.Integer(required=False, allow_none=True)


class TestMarkRowSchema(Schema):
    student_id = fields.Integer(required=True)
    obtained_marks = fields.Decimal(required=True, allow_none=True)   # null means absent


class ClassTestMarksSchema(Schema):
    marks = fields.List(fields.Nested(TestMarkRowSchema), required=True)


# ---------------- Timetable

class TimetableSlotSchema(Schema):
    day = fields.Integer(required=True, validate=validate.Range(min=1, max=6))
    period = fields.Integer(required=True, validate=validate.Range(min=1, max=8))
    subject_id = fields.Integer(required=True, allow_none=True)   # null empties the period
