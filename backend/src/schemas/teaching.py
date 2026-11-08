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


# ---------------- The section's syllabus (written by its subject teacher)

class SectionChapterSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, allow_none=True)


class UpdateSectionChapterSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, allow_none=True)


class TopicSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    planned_date = fields.Date(required=False, allow_none=True)


class UpdateTopicSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    planned_date = fields.Date(required=False, allow_none=True)


class TopicDoneSchema(Schema):
    done = fields.Boolean(required=True)


class MoveSchema(Schema):
    direction = fields.String(required=True, validate=validate.OneOf(["up", "down"]))


# ---------------- Diary

class DiaryEntrySchema(Schema):
    subject_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    classwork = fields.String(required=False, allow_none=True, validate=validate.Length(max=5000))
    homework = fields.String(required=False, allow_none=True, validate=validate.Length(max=5000))
    topic_id = fields.Integer(required=False, allow_none=True)   # written from this syllabus topic


# ---------------- Class tests

class ClassTestSchema(Schema):
    section_id = fields.Integer(required=True)
    subject_id = fields.Integer(required=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    date = fields.Date(required=True)
    total_marks = fields.Decimal(required=True, validate=validate.Range(min=1, max=999))
    chapter_id = fields.Integer(required=False, allow_none=True)
    topic_id = fields.Integer(required=False, allow_none=True)   # the syllabus topic it tests


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
    day = fields.Integer(required=True, validate=validate.Range(min=1, max=7))
    period = fields.Integer(required=True, validate=validate.Range(min=1, max=12))
    subject_id = fields.Integer(required=True, allow_none=True)   # null empties the period
    # Optional: who teaches it. A different teacher becomes the section's teacher of that subject.
    teacher_id = fields.Integer(required=False, allow_none=True)


class BellPeriodSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    start_time = fields.String(required=True)    # "08:00"
    end_time = fields.String(required=True)
    is_break = fields.Boolean(required=False, load_default=False)


class TimetableSettingsSchema(Schema):
    days = fields.List(fields.Integer(), required=True)                  # 1 = Monday ... 7 = Sunday
    periods = fields.List(fields.Nested(BellPeriodSchema), required=True, validate=validate.Length(max=20))
