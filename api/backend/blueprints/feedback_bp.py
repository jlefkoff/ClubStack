from flask import Blueprint, jsonify, request

feedback_bp = Blueprint("feedback", __name__)


# GET /feedback - Review feedback
@feedback_bp.route("/", methods=["GET"])
def review_feedback():
    return jsonify({"feedback": "List of feedback (stub)"}), 200


# POST /feedback - Submit feedback
@feedback_bp.route("/", methods=["POST"])
def submit_feedback():
    return jsonify({"message": "Feedback submitted (stub)"}), 201
