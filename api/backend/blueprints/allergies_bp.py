from flask import Blueprint, jsonify, make_response, request
from backend.utils.db_utils import execute_query, execute_update

allergies_bp = Blueprint("allergies", __name__)


# GET /allergies/report - Get food allergy report
@allergies_bp.route("/report", methods=["GET"])
def get_allergy_report():
    """
    Get food allergy report with member counts
    ---
    tags:
      - allergies
    summary: Get allergy report
    description: Returns a report of all allergies with count of affected members
    responses:
      200:
        description: Allergy report retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              AllergyName:
                type: string
                description: Name of the allergy
                example: "Peanuts"
              MemberCount:
                type: integer
                description: Number of members with this allergy
                example: 5
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
      SELECT DISTINCT a.Name as AllergyName, COUNT(au.UserID) as MemberCount
      FROM Allergy a
      LEFT OUTER JOIN AllergyUsers au ON a.ID = au.AllergyID
      GROUP BY a.ID, a.Name
      ORDER BY MemberCount DESC;
    """
    return execute_query(query)


# POST /allergies - Create allergy
@allergies_bp.route("/", methods=["POST"])
def create_allergy():
    """
    Create a new allergy
    ---
    tags:
      - allergies
    summary: Create new allergy
    description: Creates a new allergy type in the system
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: AllergyCreate
          required:
            - Name
          properties:
            Name:
              type: string
              description: Name of the allergy
              example: "Shellfish"
    responses:
      201:
        description: Allergy created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Allergy created"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Name is required"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    data = request.get_json()
    name = data.get("Name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    query = "INSERT INTO Allergy (Name) VALUES (%s);"
    params = (name,)
    result = execute_update(query, params)
    return jsonify({"message": "Allergy created"}), 201


# GET /allergies - Get existing allergies
@allergies_bp.route("/", methods=["GET"])
def get_allergies():
    """
    Get all allergies
    ---
    tags:
      - allergies
    summary: Get all allergies
    description: Returns a list of all allergy types in the system
    responses:
      200:
        description: Allergies retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              ID:
                type: integer
                description: Unique identifier for the allergy
                example: 1
              Name:
                type: string
                description: Name of the allergy
                example: "Peanuts"
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
        SELECT  ID,
                Name
        FROM Allergy
    """
    return execute_query(query)