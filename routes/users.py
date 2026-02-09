from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    identity = get_jwt_identity()
    return jsonify({"identity": identity}), 200
