from flask import Blueprint, jsonify, request
from backend.utils.db_utils import execute_query, execute_update
from backend.db_connection import db
from flask import current_app as app, make_response

budget_bp = Blueprint("budget", __name__)


# GET /budget - Show all budgets
@budget_bp.route("/", methods=["GET"])
def show_budgets():
    query = """
      SELECT B.ID as BudgetID, FiscalYear, Status, M.FirstName as AuthorFirstName,
      M.LastName as AuthorLastName, A.FirstName as ApprovedByFirstName,
      A.LastName as ApprovedByLastName
      FROM Budget B
      JOIN Member M ON B.Author = M.ID
      LEFT OUTER JOIN Member A ON B.ApprovedBy = A.ID;
    """
    return execute_query(query)


# POST /budget - Create new budget proposal
@budget_bp.route("/", methods=["POST"])
def create_budget():
    # Fetch budget info with author and approver details
    cursor = db.get_db().cursor()
    # Fetch budget info
    budget_query = """
      SELECT B.ID as BudgetID, FiscalYear, Status,
       M.ID as AuthorID, M.FirstName as AuthorFirstName, M.LastName as AuthorLastName,
       A.ID as ApprovedByID, A.FirstName as ApprovedByFirstName, A.LastName as ApprovedByLastName
      FROM Budget B
      JOIN Member M ON B.Author = M.ID
      LEFT OUTER JOIN Member A ON B.ApprovedBy = A.ID
      WHERE B.ID = %s;
    """
    cursor.execute(budget_query, (id,))
    budget_row = cursor.fetchone()
    if not budget_row:
        return jsonify({"error": "Budget not found"}), 404

    # Fetch accounts for this budget
    accounts_query = """
      SELECT ID, AcctCode, AcctTitle
      FROM BudgetAccount
      WHERE Budget = %s;
    """
    cursor.execute(accounts_query, (id,))
    accounts = cursor.fetchall()

    response = {
        "ID": budget_row["BudgetID"],
        "FiscalYear": budget_row["FiscalYear"],
        "Status": budget_row["Status"],
        "Author": {
            "ID": budget_row["AuthorID"],
            "FirstName": budget_row["AuthorFirstName"],
            "LastName": budget_row["AuthorLastName"],
        },
        "ApprovedBy": (
            {
                "ID": budget_row["ApprovedByID"],
                "FirstName": budget_row["ApprovedByFirstName"],
                "LastName": budget_row["ApprovedByLastName"],
            }
            if budget_row["ApprovedByID"]
            else None
        ),
        "Accounts": [
            {
                "ID": acct["ID"],
                "AcctCode": acct["AcctCode"],
                "AcctTitle": acct["AcctTitle"],
            }
            for acct in accounts
        ],
    }
    return jsonify(response), 200


# GET /budget/<id>/report - Budget + active member analysis
@budget_bp.route("/<int:id>/report", methods=["GET"])
def budget_report(id):
    query = """
    SELECT * FROM Budget WHERE ID = %s;
    """
    return execute_query(query, (id,))


# PUT /budget/<id>/approve - Approve submitted budget
@budget_bp.route("/<int:id>/approve", methods=["PUT"])
def approve_budget(id):
    data = request.get_json()
    approved_by = data.get("ApprovedBy")

    if not approved_by:
        return jsonify({"error": "ApprovedBy is required"}), 400

    # Check if budget exists and is in SUBMITTED status
    cursor = db.get_db().cursor()
    cursor.execute("SELECT Status FROM Budget WHERE ID = %s", (id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": "Budget not found"}), 404
    if row["Status"] != "SUBMITTED":
        return jsonify({"error": "Budget is not in SUBMITTED status"}), 400

    # Update budget status to APPROVED
    update_query = """
      UPDATE Budget
      SET Status = 'APPROVED', ApprovedBy = %s
      WHERE ID = %s;
    """
    execute_update(update_query, (approved_by, id))
    return (
        jsonify(
            {
                "message": "Budget approved successfully",
                "budget_id": id,
                "status": "APPROVED",
            }
        ),
        200,
    )


# DELETE /budget/<id> - Delete budget proposal
@budget_bp.route("/<int:id>", methods=["DELETE"])
def delete_budget(id):
    query = "DELETE FROM Budget WHERE ID = %s"
    execute_update(query, (id,))
    return (jsonify({"message": "Budget deleted successfully"}),)


# DELETE /budget/<id>/<account_id> - Delete budget account
@budget_bp.route("/<int:id>/<int:account_id>", methods=["DELETE"])
def delete_budget_account(id, account_id):
    query = "DELETE FROM BudgetAccount WHERE Budget = %s AND ID = %s"
    execute_update(query, (id, account_id))
    return jsonify({"message": "Budget account deleted successfully"}), 200
