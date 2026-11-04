from marshmallow import Schema, fields, validate

class AnnouncementSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content = fields.String(required=True)
    target_audience = fields.String(validate=validate.OneOf(["all", "teachers", "students"]))
    section_id = fields.Integer(required=False)   # preferred: names can repeat
    section_name = fields.String(required=False)
    teacher_id = fields.Integer(dump_only=True)
    # Post as the section's class incharge (a class announcement); only the incharge may
    as_incharge = fields.Boolean(required=False, load_default=False)

class UpdateAnnouncementSchema(Schema):
    section_id = fields.Integer(required=False)
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    content = fields.String(required=False)
    target_audience = fields.String(required=False, validate=validate.OneOf(["all", "teachers", "students"]))
    section_name = fields.String(required=False)
    teacher_id = fields.Integer(dump_only=True)

class AdminAnnouncementSchema(Schema):
    """An announcement from the admin: for everyone, teachers or students, and for the whole
    school (no class or section), one class (all its sections) or one section."""
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content = fields.String(required=True, validate=validate.Length(min=1))
    target_audience = fields.String(required=False, load_default="all", validate=validate.OneOf(["all", "teachers", "students"]))
    class_id = fields.Integer(required=False, allow_none=True, load_default=None)
    section_id = fields.Integer(required=False, allow_none=True, load_default=None)


class UpdateAdminAnnouncementSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    content = fields.String(required=False, validate=validate.Length(min=1))
    target_audience = fields.String(required=False, validate=validate.OneOf(["all", "teachers", "students"]))
    class_id = fields.Integer(required=False, allow_none=True)
    section_id = fields.Integer(required=False, allow_none=True)
