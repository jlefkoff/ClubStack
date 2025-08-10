from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query

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
    return jsonify({"message": "Submit reimbursement (stub)"}), 201


# GET /reimbursements/<int:id> - Get a specific reimbursement
@reimbursements_bp.route("/<int:id>", methods=["GET"])
def get_reimbursement(id):
    query = f"""
    SELECT * FROM Reimbursement JOIN ReimbursementItem
      ON Reimbursement.ID = ReimbursementItem.Reimbursement
      WHERE Reimbursement.ID = {id};
    """
    return execute_query(query)


# PUT /reimbursements/<int:id> - Update a reimbursement status
@reimbursements_bp.route("/<int:id>", methods=["PUT"])
def update_reimbursement_status(id):
    return (
        jsonify(
            {"reimbursement_id": id, "message": "Reimbursement status updated (stub)"}
        ),
        200,
    )


# PUT /reimbursements/<int:id>/approve - Approve reimbursement
@reimbursements_bp.route("/<int:id>/approve", methods=["PUT"])
def approve_reimbursement(id):
    return (
        jsonify({"reimbursement_id": id, "message": "Reimbursement approved (stub)"}),
        200,
    )
