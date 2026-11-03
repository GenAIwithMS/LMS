from flask import Blueprint,request,jsonify
from src.models import Admin
from flask_jwt_extended import jwt_required , get_jwt

admin_bp = Blueprint("admin",__name__)


# There is no route to create an admin. The LMS has a single admin, created once
# during setup with:  python create_admin.py


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

    admin = Admin.query.get(admin_id)
    if not admin:
        return jsonify({
            "message": "Admin not found",
            "status": "failed"
        }), 404

    return jsonify({
        "id": admin.id,
        "name": admin.name,
        "username": admin.username,
        "email": admin.email
    })


    