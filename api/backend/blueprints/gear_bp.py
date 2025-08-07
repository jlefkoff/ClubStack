########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################
from backend.db_connection import db
from flask import Blueprint, current_app, jsonify, make_response, request

# ------------------------------------------------------------
# Create a new Blueprint object, which is a collection of
# routes.
gear_bp = Blueprint("gear", __name__)


# ------------------------------------------------------------
# GET /rental-items - Browse available gear
@gear_bp.route("/rental-items", methods=["GET"])
def get_rental_items():
    # Stub: Return empty list or placeholder data
    return jsonify([]), 200


# ------------------------------------------------------------
# POST /rental-items - Post new rental item
@gear_bp.route("/rental-items", methods=["POST"])
def post_rental_item():
    # Stub: Accept posted data and return success
    return jsonify({"message": "Rental item created (stub)"}), 201


# ------------------------------------------------------------
# GET /rental-items/<id> - Browse specific item
@gear_bp.route("/rental-items/<int:item_id>", methods=["GET"])
def get_rental_item(item_id):
    # Stub: Return placeholder item
    return jsonify({"id": item_id, "name": "Stub Item"}), 200


# ------------------------------------------------------------
# PUT /rental-items/<id>/toggle-avail - Mark item unavailable
@gear_bp.route("/rental-items/<int:item_id>/toggle-avail", methods=["PUT"])
def toggle_rental_item_avail(item_id):
    # Stub: Toggle availability
    return jsonify({"id": item_id, "available": False}), 200


# ------------------------------------------------------------
# POST /gear-reservations - Reserve gear
@gear_bp.route("/gear-reservations", methods=["POST"])
def reserve_gear():
    # Stub: Accept reservation and return success
    return jsonify({"message": "Gear reserved (stub)"}), 201


# ------------------------------------------------------------
# GET /gear-reservations/report - Gear ROI report
@gear_bp.route("/gear-reservations/report", methods=["GET"])
def gear_roi_report():
    # Stub: Return placeholder report
    return jsonify({"report": "ROI report (stub)"}), 200
