from src.models import Admin
from src.services.users import is_email_taken, is_username_taken
from flask import jsonify
from src.db import db

def add_admin(name, email, username, password):
    if is_email_taken(email):
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    if is_username_taken(username):
        return jsonify({
            "message":"Username already exists",
            "status":"failed"
        }), 400


    new_admin = Admin(
        name=name,
        email=email,
        username=username,
    )
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({
        "message":"admin added successfully",
        "status":"success"
    }), 201