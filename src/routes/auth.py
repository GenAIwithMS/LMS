from flask import Blueprint,request,jsonify
from src.models.admin import Admin
from src.models.student import Student
from src.models.teacher import Teacher
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from src.schemas.auth_schema import loginSchema

auth = Blueprint('auth', __name__)


@auth.route('/api/login', methods=['POST'])
def login():
    try:
        data = loginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "status": False,
            "message": "email and password required"
        }), 400
    

    role = ''
    user = Admin.query.filter_by(email=email).first()
    if user:
        role = 'admin'
    
    if not role or not user:
        user = Teacher.query.filter_by(email=email).first()
        if user:
            role = 'teacher'

    if not role or not user:
        user = Student.query.filter_by(email=email).first()
        if user:
            role = 'student'
    

    if not user:
        return jsonify({
            "status": False,
            "message": "Invalid email"
        }), 401
    if not user.check_password(password):
        return jsonify({
            "status": False,
            "message": "Invalid password"
        }), 401
    
    token = create_access_token(identity=str(user),additional_claims={"role":role})
    return jsonify({
        "status": True,
        "message": "Login successful",
        "token": token,
        "Result": str(user)
    })

