from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query, execute_update

reimbursements_bp = Blueprint("reimbursements", __name__)


# GET /reimbursements - Reimbursement Overview
@reimbursements_bp.route("/", methods=["GET"])
def reimbursement_overview():
    query = """
    SELECT * FROM Reimbursement;
    """
    return execute_query(query)


# POST /reimbursements - Submit reimbursement
@reimbursements_bp.route("/", methods=["POST"])
def submit_reimbursement():
    data = request.json
    if (
        not data
        or "member_id" not in data
        or "description" not in data
        or "items" not in data
    ):
        return jsonify({"error": "Invalid data"}), 400

    member_id = data["member_id"]
    description = data["description"]
    total = data["total"]
    items = data["items"]

    if not isinstance(items, list) or not items:
        return jsonify({"error": "Items must be a non-empty list"}), 400

    # Prepare SQL for inserting reimbursement
    query = """
    INSERT INTO Reimbursement (MemberID, Total, Type) VALUES (%s, %s, %s);
    """
    reimbursement_id = execute_update(query, (member_id, total, description))

    # Insert each item into ReimbursementItem
    item_values = ", ".join(
        f"({reimbursement_id}, '{item['description']}', {item['price']})"
        for item in items
    )
    item_query = f"""
    INSERT INTO ReimbursementItem (Reimbursement, Description, Price)
    VALUES {item_values};
    """
    execute_update(item_query)
    return jsonify({"reimbursement_id": reimbursement_id, "status": "Pending"}), 201


# GET /reimbursements/<int:id> - Get a specific reimbursement
@reimbursements_bp.route("/<int:id>", methods=["GET"])
def get_reimbursement(id):
    query = f"""
    SELECT * FROM Reimbursement JOIN ReimbursementItem
      ON Reimbursement.ID = ReimbursementItem.Reimbursement
      WHERE Reimbursement.ID = {id};
    """
    return execute_query(query)


# PUT /reimbursements/<int:id>/approve - Approve reimbursement
@reimbursements_bp.route("/<int:id>/approve", methods=["PUT"])
def approve_reimbursement(id):
    query = """
    UPDATE Reimbursement SET Status = 'APPROVED' WHERE ID = %s;
    """
    result = execute_query(query, (id,))

    if result:
        return jsonify({"message": "Reimbursement approved successfully"}), 200
    else:
        return jsonify({"error": "Reimbursement not found"}), 404
