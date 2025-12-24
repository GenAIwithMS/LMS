from flask import Blueprint,request,jsonify
from src.schemas.auth_schema import RegisterAdminSchema
from marshmallow import ValidationError
from src.db import db
from werkzeug.utils import secure_filename
from src.services.admin import add_admin
import os

register_bp = Blueprint("register",__name__)

@register_bp.route("/api/register", methods=["POST"])
def register_admin():
    try:
        data = RegisterAdminSchema().load(request.form)
    except ValidationError as e:
        return jsonify(e.messages), 400

    file = request.files.get("image")
    filename = secure_filename(file.filename)

    if not os.path.exists("static/images"):
        os.makedirs("static/images")

    file_path = f"static/images/{filename}"

    file.save(file_path)
    result = add_admin(
        name=data["name"],
        email=data["email"],
        username=data["username"],
        password_hash=data["password"],
        userrole = data.get(["userrole"]),
        image=filename
    )
    return result


