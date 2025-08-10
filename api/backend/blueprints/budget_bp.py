from flask import Blueprint, jsonify, request
from backend.utils.db_utils import execute_query, execute_update
from backend.db_connection import db
from flask import current_app as app, make_response

budget_bp = Blueprint("budget", __name__)


# GET /budget - Show all budgets
@budget_bp.route("/", methods=["GET"])
def show_budgets():
    """
    Get all budgets
    ---
    tags:
      - budgets
    summary: Get all budgets
    description: Returns a list of all budget proposals in the system
    responses:
      200:
        description: Budgets retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              ID:
                type: integer
                description: Unique identifier for the budget
                example: 1
              FiscalYear:
                type: integer
                description: Fiscal year for the budget
                example: 2024
              Status:
                type: string
                description: Current status of the budget
                example: "APPROVED"
              Author:
                type: integer
                description: ID of the member who created the budget
                example: 5
              ApprovedBy:
                type: integer
                description: ID of the member who approved the budget
                example: 2
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
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
    """
    Create a new budget proposal
    ---
    tags:
      - budgets
    summary: Create new budget proposal
    description: Creates a new budget proposal for a fiscal year
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: BudgetCreate
          required:
            - FiscalYear
            - Author
          properties:
            FiscalYear:
              type: integer
              description: Fiscal year for the budget
              example: 2024
            Author:
              type: integer
              description: ID of the member creating the budget
              example: 5
            Status:
              type: string
              description: Initial status of the budget
              example: "SUBMITTED"
              enum: ["SUBMITTED", "APPROVED", "PAST"]
    responses:
      201:
        description: Budget created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Budget proposal created"
            budget_id:
              type: integer
              example: 15
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
              example: "FiscalYear and Author are required"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    return jsonify({"message": "Create new budget proposal (stub)"}), 201


# GET /budget/<id> - Get existing budget data
@budget_bp.route("/<int:id>", methods=["GET"])
def get_budget(id):
    """
    Get budget by ID
    ---
    tags:
      - budgets
    summary: Get budget by ID
    description: Returns detailed information about a specific budget including accounts
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Budget ID
        example: 1
    responses:
      200:
        description: Budget retrieved successfully
        schema:
          type: object
          properties:
            ID:
              type: integer
              description: Budget ID
              example: 1
            FiscalYear:
              type: integer
              description: Fiscal year
              example: 2024
            Status:
              type: string
              description: Budget status
              example: "APPROVED"
            Author:
              type: object
              properties:
                ID:
                  type: integer
                  example: 5
                FirstName:
                  type: string
                  example: "John"
                LastName:
                  type: string
                  example: "Doe"
            ApprovedBy:
              type: object
              properties:
                ID:
                  type: integer
                  example: 2
                FirstName:
                  type: string
                  example: "Jane"
                LastName:
                  type: string
                  example: "Smith"
            Accounts:
              type: array
              items:
                type: object
                properties:
                  ID:
                    type: integer
                    example: 10
                  AcctCode:
                    type: string
                    example: "GEAR001"
                  AcctTitle:
                    type: string
                    example: "Equipment & Gear"
      404:
        description: Budget not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Budget not found"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
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
      "ApprovedBy": {
        "ID": budget_row["ApprovedByID"],
        "FirstName": budget_row["ApprovedByFirstName"],
        "LastName": budget_row["ApprovedByLastName"],
      } if budget_row["ApprovedByID"] else None,
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
    """
    Get budget analysis report
    ---
    tags:
      - budgets
    summary: Get budget analysis report
    description: Returns detailed budget analysis including spending breakdown and active member metrics
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Budget ID
        example: 1
    responses:
      200:
        description: Budget report generated successfully
        schema:
          type: object
          properties:
            BudgetInfo:
              type: object
              properties:
                ID:
                  type: integer
                  example: 1
                FiscalYear:
                  type: integer
                  example: 2024
                Status:
                  type: string
                  example: "APPROVED"
            SpendingBreakdown:
              type: array
              items:
                type: object
                properties:
                  Category:
                    type: string
                    example: "Equipment"
                  Budgeted:
                    type: number
                    example: 5000.00
                  Spent:
                    type: number
                    example: 3250.75
                  Remaining:
                    type: number
                    example: 1749.25
            ActiveMemberMetrics:
              type: object
              properties:
                TotalMembers:
                  type: integer
                  example: 150
                ActiveMembers:
                  type: integer
                  example: 125
                CostPerMember:
                  type: number
                  example: 45.50
      404:
        description: Budget not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Budget not found"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    return (
        jsonify({"budget_id": id, "report": "Budget + active member analysis (stub)"}),
        200,
    )


# PUT /budget/<id>/approve - Approve submitted budget
@budget_bp.route("/<int:id>/approve", methods=["PUT"])
def approve_budget(id):
    """
    Approve budget proposal
    ---
    tags:
      - budgets
    summary: Approve budget proposal
    description: Approves a submitted budget proposal and updates its status
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Budget ID to approve
        example: 1
      - in: body
        name: body
        required: true
        schema:
          id: BudgetApprove
          required:
            - ApprovedBy
          properties:
            ApprovedBy:
              type: integer
              description: ID of the member approving the budget
              example: 2
    responses:
      200:
        description: Budget approved successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Budget approved successfully"
            budget_id:
              type: integer
              example: 1
            status:
              type: string
              example: "APPROVED"
      400:
        description: Invalid input or budget cannot be approved
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Budget is not in SUBMITTED status"
      404:
        description: Budget not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Budget not found"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    return jsonify({"budget_id": id, "message": "Budget approved (stub)"}), 200
