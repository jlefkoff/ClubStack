from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query

events_bp = Blueprint("events", __name__)


# GET /events - List all events
@events_bp.route("/", methods=["GET"])
def get_events():
    query = """
    SELECT * FROM Event;
    """
    return execute_query(query)

# GET /events/<id> - Get specific event
@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    query = f"""
    SELECT * FROM Event WHERE ID = {event_id};
    """
    return execute_query(query)


# POST /events - Create new event
@events_bp.route("/", methods=["POST"])
def post_event():
    return jsonify({"message": "Event created (stub)"}), 201


# PUT /events/<id> - Update event
@events_bp.route("/<int:event_id>", methods=["PUT"])
def put_event(event_id):
    return jsonify({"message": f"Event {event_id} updated (stub)"}), 200


# GET /events/<id>/roster - Get event roster
@events_bp.route("/<int:event_id>/roster", methods=["GET"])
def get_event_roster(event_id):
    return jsonify({"event_id": event_id, "roster": []}), 200


# GET /events/report - Events report
@events_bp.route("/report", methods=["GET"])
def events_report():
    return jsonify({"report": "Events report (stub)"}), 200


# POST /rsvp - RSVP to an event
@events_bp.route("/rsvp", methods=["POST"])
def post_rsvp():
    return jsonify({"message": "RSVP recorded (stub)"}), 201
