from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query, execute_update

feedback_bp = Blueprint("feedback", __name__)


# GET /feedback - Review feedback
@feedback_bp.route("/", methods=["GET"])
def review_feedback():
    query = """
    SELECT * FROM Feedback;
    """
    return execute_query(query)


# POST /feedback - Submit feedback
@feedback_bp.route("/", methods=["POST"])
def submit_feedback():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Required fields
    required_fields = ["member_id", "rating", "feedback_text", "anonymous"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field} is required"}), 400

    # Insert feedback into the database
    query = """
    INSERT INTO Feedback (Member, Rating, Description, Anonymous)
    VALUES (%s, %s, %s, %s);
    """
    params = (
        data["member_id"],
        data["rating"],
        data["feedback_text"],
        data["anonymous"],
    )
    execute_update(query, params)

    return jsonify({"message": "Feedback submitted successfully"}), 201
