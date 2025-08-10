########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################
from backend.db_connection import db
from backend.utils.db_utils import execute_query, execute_update
from flask import Blueprint, current_app, jsonify, make_response, request

# ------------------------------------------------------------
# Create a new Blueprint object, which is a collection of
# routes.
gear_bp = Blueprint("gear", __name__)

# ------------------------------------------------------------
# GET / - Browse available gear
@gear_bp.route("/", methods=["GET"])
def get_rental_items():
    # Stub: Return empty list or placeholder data
    query = """
    SELECT * FROM RentalItem;
    """
    return execute_query(query)

# ------------------------------------------------------------
# POST /rental-items - Post new rental item
@gear_bp.route("/", methods=["POST"])
def post_rental_item():
    data = request.json
    query = """
    INSERT INTO RentalItem (Name, Price, Location, Quantity, Size, Status)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    params = (data["name"], data["price"], data["location"], data["quantity"], data["size"], "AVAILABLE")
    return(execute_update(query, params))


# ------------------------------------------------------------
# GET /rental-items/<id> - Browse specific item
@gear_bp.route("/<int:item_id>", methods=["GET"])
def get_rental_item(item_id):
    query = """
    SELECT * FROM RentalItem WHERE ID = %s;
    """
    return execute_query(query, (item_id,))

# ------------------------------------------------------------
# PUT /rental-items/<id>/toggle-avail - Mark item unavailable
@gear_bp.route("/rental-items/<int:item_id>/toggle-avail", methods=["PUT"])
def toggle_rental_item_avail(item_id):
    # Stub: Toggle availability
    return jsonify({"id": item_id, "available": False}), 200


# ------------------------------------------------------------
# POST /gear-reservations - Reserve gear
@gear_bp.route("/reservation", methods=["POST"])
def reserve_gear():
    data = request.json
    query = """
    INSERT INTO GearReservation (Member, CheckoutDate, ReturnDate)
    VALUES (%s, %s, %s);
    """
    params = (data["user_id"], data["start_date"], data["end_date"])
    execute_update(query, params)
    # Now do the joiner-table insert
    query = """
    INSERT INTO GearReservationItems (Reservation, Item)
    VALUES (LAST_INSERT_ID(), %s);
    """
    params = (data["item_id"],)
    execute_update(query, params)

    return jsonify({"message": "Gear reserved"}), 201


# ------------------------------------------------------------
# GET /gear-reservations/report - Gear ROI report
@gear_bp.route("/gear-reservations/report", methods=["GET"])
def gear_roi_report():
    # Stub: Return placeholder report
    return jsonify({"report": "ROI report (stub)"}), 200
