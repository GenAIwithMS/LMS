from src.models.admin import Admin
from flask import jsonify
from src.db import db
import os

def add_admin(name, email, username, password, image):

    file = image
    if file:
        filepath = f"src/static/images/{file.filename}"
        if not os.path.exists("src/static/images/"):
            os.makedirs("src/static/images/")
        file.save(filepath)

    new_admin = Admin(
        name=name,
        email=email,
        username=username,
        image=filepath
    )
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({
        "message":"admin added successfully",
        "status":"success"
    })