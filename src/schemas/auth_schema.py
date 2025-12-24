from marshmallow import Schema, fields, validate, validates
from src.models.admin import Admin


# class LoginSchema(Schema):
#     email = fields.Email(required=True)
#     password = fields.String(required=True, validate=validate.Length(min=6,max=8))

#     @validates('email')
#     def validate_email(self, value, **kwargs):
#         admin = Admin.query.filter_by(email=value).first()
#         if not admin:
#             raise validate.ValidationError('entered email does not exist.')

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
    # section_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(required=True)
    password_hash = fields.String(required=True, validate=validate.Length(min=6))

class RegisterStudentSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    username = fields.String(required=True, validate=validate.Length(min=3, max=100))
    # section_id = fields.String(required=True, validate=validate.Length(min=1, max=50))
    section_id = fields.Integer(required=True)
    teacher_id = fields.Integer(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class loginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

