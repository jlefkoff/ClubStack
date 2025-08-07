from flask import Blueprint, jsonify, request

allergies_bp = Blueprint("allergies", __name__)


# GET /allergies/report - Get food allergy report
@allergies_bp.route("/report", methods=["GET"])
def get_allergy_report():
    return jsonify({"report": "Food allergy report (stub)"}), 200


# POST /allergies - Create allergy
@allergies_bp.route("/", methods=["POST"])
def create_allergy():
    return jsonify({"message": "Allergy created (stub)"}), 201


# GET /allergies - Get existing allergies
@allergies_bp.route("/", methods=["GET"])
def get_allergies():
    return jsonify({"allergies": "List of allergies (stub)"}), 200
