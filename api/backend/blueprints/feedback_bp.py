from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query

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
    return jsonify({"message": "Feedback submitted (stub)"}), 201
