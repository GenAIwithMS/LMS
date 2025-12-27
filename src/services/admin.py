from src.models.admin import Admin
from flask import jsonify
from src.db import db
import os

def add_admin(name, email, username, password):
    existing_email = Admin.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({
            "message":"Email already exists",
            "status":"failed"
        }), 400
    existing_username = Admin.query.filter_by(username=username).first()
    if existing_username:
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