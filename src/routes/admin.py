from flask import Blueprint,request,jsonify
from src.models.admin import Admin
# from src.db import db
from flask_jwt_extended import jwt_required , get_jwt
from src.services.admin import add_admin
# from src.services.user import add_user
from src.schemas.auth_schema import RegisterAdminSchema
from marshmallow import ValidationError
import os 

admin_bp = Blueprint("admin",__name__)


@admin_bp.route("/api/add-admin", methods=["POST"])
def add_adm():

    try:
        data = RegisterAdminSchema().load(request.form)
    except ValidationError as e:
        return jsonify(e.messages), 400
    

    result = add_admin(
        name=data["name"],
        email=data["email"],
        username=data["username"],
        password=data["password"],
        image=request.files.get("image")
    )
    
    return result

@admin_bp.route("/api/get/admin", methods=["GET"])
@jwt_required()
def get_admin():

    if get_jwt()["role"] != "admin":
        return jsonify({
            "message":"Only admin can access admin details"
        }),403

    admin_id = request.args.get("id", type=int)

    if admin_id is None:
        all_admin = Admin.query.all()

        result = []
        for std in all_admin:
            result.append({
                    "id": std.id,
                    "username": std.username                    
                })
        return jsonify(result)


    