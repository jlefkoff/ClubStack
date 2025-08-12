from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query
from backend.db_connection import db

members_bp = Blueprint("members", __name__)


# POST /members - Create new member
@members_bp.route("/", methods=["POST"])
def post_member():
    return jsonify({"message": "Member created (stub)"}), 201


# GET /members - View all members
@members_bp.route("/", methods=["GET"])
def get_members():
    cursor = db.get_db().cursor()
    # Fetch all members
    query = """
    SELECT * FROM Member;
    """
    cursor.execute(query)
    members = cursor.fetchall()
    # Build a mapping of member_id -> list of allergy names
    allergies_query = """
    SELECT M.ID as member_id, GROUP_CONCAT(A.Name) as Allergies
    FROM Member M
    LEFT JOIN AllergyUsers AU ON M.ID = AU.UserID
    LEFT JOIN Allergy A ON AU.AllergyID = A.ID
    GROUP BY M.ID;
    """
    cursor.execute(allergies_query)
    allergies_map = {row["member_id"]: row["Allergies"] or "" for row in cursor.fetchall()}

    # Attach allergies to each member
    members_with_allergies = []
    for member in members:
      member_id = member["ID"]
      member["Allergies"] = allergies_map.get(member_id, "")
      members_with_allergies.append(member)

    return jsonify({"members": members_with_allergies}), 200

# GET /members/<int:member_id> - View specific member
@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
  cursor = db.get_db().cursor()
  # Fetch member
  member_query = """
  SELECT * FROM Member WHERE ID = %s;
  """
  cursor.execute(member_query, (member_id,))
  member = cursor.fetchone()
  if not member:
    return jsonify({"error": "Member not found"}), 404

  # Fetch allergies for this member
  allergies_query = """
  SELECT GROUP_CONCAT(A.Name) as Allergies
  FROM AllergyUsers AU
  LEFT JOIN Allergy A ON AU.AllergyID = A.ID
  WHERE AU.UserID = %s;
  """
  cursor.execute(allergies_query, (member_id,))
  allergies_row = cursor.fetchone()
  member["Allergies"] = allergies_row["Allergies"] or ""

  return jsonify({"member": member}), 200

# PUT /members/<int:member_id>/activate - Activate/Renew member with payment
@members_bp.route("/<int:member_id>/activate", methods=["PUT"])
def activate_member(member_id):
    return jsonify(
        {"message": f"Member {member_id} activated/renewed (stub)"}), 200
