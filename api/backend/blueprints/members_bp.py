from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query

members_bp = Blueprint("members", __name__)


# POST /members - Create new member
@members_bp.route("/", methods=["POST"])
def post_member():
    return jsonify({"message": "Member created (stub)"}), 201


# GET /members - View all members
@members_bp.route("/", methods=["GET"])
def get_members():
    query = """
    SELECT * FROM Member;
    """
    return execute_query(query)

# GET /members/<int:member_id> - View specific member
@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    query = f"""
    SELECT * FROM Member WHERE ID = {member_id};
    """
    return execute_query(query)

# PUT /members/<int:member_id>/activate - Activate/Renew member with payment
@members_bp.route("/<int:member_id>/activate", methods=["PUT"])
def activate_member(member_id):
    return jsonify(
        {"message": f"Member {member_id} activated/renewed (stub)"}), 200
