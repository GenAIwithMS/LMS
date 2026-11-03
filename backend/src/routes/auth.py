from flask import Blueprint,request,jsonify
from src.models import Admin,Teacher,Student
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from src.schemas import loginSchema, UpdateMyUsernameSchema, ChangeMyPasswordSchema
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.db import db
from src.services.users import is_username_taken

auth_bp = Blueprint('auth', __name__)


def make_token(user, role):
    """Create a login token with the user's details in it."""
    additional_claims = {
        "role": role,
        "name": user.name,
        "email": user.email,
        "username": user.username if hasattr(user, 'username') else user.email
    }
    return create_access_token(identity=str(user.id), additional_claims=additional_claims)


def get_logged_in_user():
    """Return the account of whoever sent this request (admin, teacher or student)."""
    token = get_jwt()
    role = token.get("role")
    user_id = int(get_jwt_identity())

    if role == "admin":
        return Admin.query.get(user_id)
    if role == "teacher":
        return Teacher.query.get(user_id)
    if role == "student":
        return Student.query.get(user_id)
    return None


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
        token = make_token(user, role)
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


@auth_bp.route("/api/account", methods=["GET"])
@jwt_required()
def get_my_account():
    """Show the logged-in user's own account details."""
    user = get_logged_in_user()
    if not user:
        return jsonify({
            "message": "Account not found",
            "status": "failed"
        }), 404

    return jsonify({
        "status": "success",
        "account": {
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role": get_jwt().get("role")
        }
    })


@auth_bp.route("/api/account/username", methods=["PUT"])
@jwt_required()
def update_my_username():
    """Let the logged-in user change their own username."""
    try:
        data = UpdateMyUsernameSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    user = get_logged_in_user()
    if not user:
        return jsonify({
            "message": "Account not found",
            "status": "failed"
        }), 404

    new_username = data["username"].strip()

    if is_username_taken(new_username, current_user=user):
        return jsonify({
            "message": "Username already exists",
            "status": "failed"
        }), 400

    user.username = new_username
    db.session.commit()

    # The old token still has the old username in it, so send a fresh one
    role = get_jwt().get("role")
    new_token = make_token(user, role)

    return jsonify({
        "message": "Username updated successfully",
        "status": "success",
        "token": new_token
    })


@auth_bp.route("/api/account/password", methods=["PUT"])
@jwt_required()
def change_my_password():
    """Let the logged-in user change their own password. They must give their current password."""
    try:
        data = ChangeMyPasswordSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    user = get_logged_in_user()
    if not user:
        return jsonify({
            "message": "Account not found",
            "status": "failed"
        }), 404

    if not user.check_password(data["current_password"]):
        return jsonify({
            "message": "Current password is incorrect",
            "status": "failed"
        }), 400

    if data["current_password"] == data["new_password"]:
        return jsonify({
            "message": "New password must be different from the current password",
            "status": "failed"
        }), 400

    user.set_password(data["new_password"])
    db.session.commit()

    return jsonify({
        "message": "Password changed successfully",
        "status": "success"
    })
