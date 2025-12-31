from flask import Blueprint,request,jsonify
from src.models.admin import Admin
from src.models.student import Student
from src.models.teacher import Teacher
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from src.schemas.auth_schema import loginSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
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
    try:
        # Include user information in JWT token
        additional_claims = {
            "role": role,
            "name": user.name,
            "email": user.email,
            "username": user.username if hasattr(user, 'username') else user.email
        }
        token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    except Exception as e:
        return jsonify({
            "message": f"you have an error: {str(e)}"
        })
    return jsonify({
        "status": True,
        "message": "Login successful",
        "token": token
    })

@auth_bp.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify(id=user_id)
