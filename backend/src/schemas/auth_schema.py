from marshmallow import Schema, fields, validate


class RegisterAdminSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    password = fields.String(required=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))

class RegisterTeacherSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    username = fields.String(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class UpdateTeacherSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=3, max=100))
    username = fields.String(required=False, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=False)
    password = fields.String(required=False, validate=validate.Length(min=6))

class RegisterStudentSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    username = fields.String(required=True, validate=validate.Length(min=3, max=100))
    section_id = fields.Integer(required=False)   # preferred: names can repeat
    section_name = fields.String(required=False)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class UpdateStudentSchema(Schema):
    section_id = fields.Integer(required=False)
    name = fields.String(required=False, validate=validate.Length(min=3, max=100))
    username = fields.String(required=False, validate=validate.Length(min=3, max=100))
    teacher_id = fields.Integer(required=False)
    section_name = fields.String(required=False)
    email = fields.Email(required=False)
    password = fields.String(required=False, validate=validate.Length(min=6))

class loginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))


class UpdateMyUsernameSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=100))

class ChangeMyPasswordSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=6))
