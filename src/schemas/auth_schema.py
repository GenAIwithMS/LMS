from marshmallow import Schema, fields, validate, validates


class RegisterAdminSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    password = fields.String(required=True, validate=validate.Length(min=6))
    image = fields.String(required=False)
    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))

class RegisterTeacherSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    subject = fields.String(required=True, validate=validate.Length(min=2, max=50))
    username = fields.String(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    student_id = fields.Integer(required=True)
    password_hash = fields.String(required=True, validate=validate.Length(min=6))

class UpdateTeacherSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=3, max=100))
    subject = fields.String(required=False, validate=validate.Length(min=2, max=50))
    username = fields.String(required=False, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=False)
    student_id = fields.Integer(required=False)
    password_hash = fields.String(required=False, validate=validate.Length(min=6))

class RegisterStudentSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    username = fields.String(required=True, validate=validate.Length(min=3, max=100))
    teacher_id = fields.Integer(required=True)
    section_id = fields.Integer(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class UpdateStudentSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=3, max=100))
    username = fields.String(required=False, validate=validate.Length(min=3, max=100))
    teacher_id = fields.Integer(required=False)
    section_id = fields.Integer(required=False)
    email = fields.Email(required=False)
    password = fields.String(required=False, validate=validate.Length(min=6))

class loginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

