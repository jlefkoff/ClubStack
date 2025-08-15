from flask import Blueprint, jsonify, make_response, request
from backend.utils.db_utils import execute_query, execute_update

allergies_bp = Blueprint("allergies", __name__)


# GET /allergies/report - Get food allergy report
@allergies_bp.route("/report", methods=["GET"])
def get_allergy_report():
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
    query = """
        SELECT  ID,
                Name
        FROM Allergy
    """
    return execute_query(query)


# DELETE /allergies/<int:allergy_id> - Delete an allergy
@allergies_bp.route("/<int:allergy_id>", methods=["DELETE"])
def delete_allergy(allergy_id):
    query = """
    DELETE FROM Allergy WHERE ID = %s;
    """
    result = execute_update(query, (allergy_id,))
    if result:
        return jsonify({"message": "Allergy deleted successfully"}), 200
    else:
        return jsonify({"error": "Allergy not found"}), 404
