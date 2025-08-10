from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query

permissions_bp = Blueprint("permissions", __name__)


# POST /permissions/<member_id> - Assign permissions
@permissions_bp.route("/<int:member_id>", methods=["POST"])
def assign_permissions(member_id):
    return (
        jsonify({"message": f"Permissions assigned to member {member_id} (stub)"}),
        201,
    )


# GET /permissions/<member_id> - Get permissions of member
@permissions_bp.route("/<int:member_id>", methods=["GET"])
def get_member_permissions(member_id):
    return jsonify({"member_id": member_id, "permissions": []}), 200


# POST /permissions - Create permission
@permissions_bp.route("/", methods=["POST"])
def create_permission():
    return jsonify({"message": "Permission created (stub)"}), 201


# GET /permissions - List all permissions
@permissions_bp.route("/", methods=["GET"])
def list_permissions():
    query = """
    SELECT * FROM Permission;
    """
    return execute_query(query)
