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
    params = (
        data["name"],
        data["price"],
        data["location"],
        data["quantity"],
        data["size"],
        "AVAILABLE",
    )
    return execute_update(query, params)


# ------------------------------------------------------------
# GET /<id> - Browse specific item
@gear_bp.route("/<int:item_id>", methods=["GET"])
def get_rental_item(item_id):
    query = """
    SELECT * FROM RentalItem WHERE ID = %s;
    """
    return execute_query(query, (item_id,))

# ------------------------------------------------------------
# DELETE /<id> - Remove specific item
@gear_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_rental_item(item_id):
    query = """
    DELETE FROM RentalItem WHERE ID = %s;
    """
    return execute_update(query, (item_id))


# ------------------------------------------------------------
# PUT /<id>/toggle-avail - Mark item unavailable
@gear_bp.route("/<int:item_id>/toggle-avail/<string:status>", methods=["PUT"])
def toggle_rental_item_avail(item_id, status):
    query = """
    UPDATE RentalItem SET Status = %s WHERE ID = %s;
    """
    return execute_update(query, (status, item_id))

# ------------------------------------------------------------
# GET /reservation/ - Get all gear reservations
@gear_bp.route("/reservation", methods=["GET"])
def get_gear_reservations():
    query = """
    SELECT * FROM GearReservation JOIN GearReservationItems ON GearReservation.ID = GearReservationItems.Reservation
         JOIN RentalItem ON GearReservationItems.Item = RentalItem.ID;
    """
    return execute_query(query)

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

    return jsonify({"message": "Gear reserved"}), 200


# ------------------------------------------------------------
# GET /reservations/<member_id> - Get all member's gear reservations
@gear_bp.route("/reservations/<int:member_id>", methods=["GET"])
def get_gear_reservation(member_id):
    query = """
    SELECT Name, CheckOutDate, ReturnDate FROM GearReservation JOIN GearReservationItems ON GearReservation.ID = GearReservationItems.Reservation
         JOIN RentalItem ON GearReservationItems.Item = RentalItem.ID
         WHERE Member = %s;
    """
    return execute_query(query, (member_id,))

# PUT /reservations/<reservation_id>/<status> - Update gear reservation status
@gear_bp.route("/reservations/<int:reservation_id>/<string:status>", methods=["PUT"])
def update_gear_reservation_status(reservation_id, status):
    query = """
    UPDATE GearReservation SET Status = %s WHERE ID = %s;
    """
    return execute_update(query, (status, reservation_id))

# DELETE /reservations/<reservation_id> - Cancel a gear reservation
@gear_bp.route("/reservations/<int:reservation_id>", methods=["DELETE"])
def delete_gear_reservation(reservation_id):
    query = """
    DELETE FROM GearReservation WHERE ID = %s;
    """
    return execute_update(query, (reservation_id,))


# ------------------------------------------------------------
# GET /gear-reservations/report - Gear ROI report
@gear_bp.route("/report", methods=["GET"])
def gear_roi_report():
    # Stub: Return placeholder report
    return jsonify({"report": "ROI report (stub)"}), 200
