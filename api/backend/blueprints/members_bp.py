from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query, execute_update
from backend.db_connection import db

members_bp = Blueprint("members", __name__)


# POST /members - Create new member
@members_bp.route("/", methods=["POST"])
def post_member():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Required fields
    required_fields = [
        "first_name",
        "last_name",
        "emer_contact_name",
        "emer_contact_phone",
    ]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field} is required"}), 400

    # Extract and validate data
    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()
    preferred_name = data.get("preferred_name")
    if preferred_name:
        preferred_name = preferred_name.strip() or None

    graduation_year = data.get("graduation_year")
    is_grad_student = bool(data.get("is_grad_student", False))
    activation_date = data.get("activation_date")

    # Car fields
    car_plate = data.get("car_plate")
    if car_plate:
        car_plate = car_plate.strip() or None

    car_state = data.get("car_state")
    if car_state:
        car_state = car_state.strip() or None

    car_pass_count = data.get("car_pass_count")

    emer_contact_name = data["emer_contact_name"].strip()
    emer_contact_phone = data["emer_contact_phone"].strip()

    # Validate car data consistency
    has_car_data = any([car_plate, car_state, car_pass_count is not None])
    if has_car_data and not all([car_plate, car_state, car_pass_count is not None]):
        return (
            jsonify(
                {
                    "error": "If providing car information, all car fields (plate, state, pass_count) are required"
                }
            ),
            400,
        )

    try:
        cursor = db.get_db().cursor()

        # Insert member
        insert_query = """
        INSERT INTO Member (
            FirstName, LastName, PreferredName, GraduationYear, 
            IsGradStudent, ActivationDate, CarPlate, CarState, 
            CarPassCount, EmerContactName, EmerContactPhone
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            first_name,
            last_name,
            preferred_name,
            graduation_year,
            is_grad_student,
            activation_date,
            car_plate,
            car_state,
            car_pass_count,
            emer_contact_name,
            emer_contact_phone,
        )

        cursor.execute(insert_query, values)
        member_id = cursor.lastrowid
        db.get_db().commit()

        return (
            jsonify({"message": "Member created successfully", "member_id": member_id}),
            201,
        )

    except Exception as e:
        db.get_db().rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


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
    allergies_map = {
        row["member_id"]: row["Allergies"] or "" for row in cursor.fetchall()
    }

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
    return jsonify({"message": f"Member {member_id} activated/renewed (stub)"}), 200
