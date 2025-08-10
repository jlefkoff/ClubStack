from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query
from backend.db_connection import db

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
  cursor = db.get_db().cursor()

  # Get event details
  event_query = """
  SELECT * FROM Event WHERE ID = %s;
  """
  cursor.execute(event_query, (event_id,))
  event_row = cursor.fetchone()
  if not event_row:
    return jsonify({"error": "Event not found"}), 404

  # Get roster for the event
  roster_query = """
  SELECT ER.DateRegistered, ER.Waitlisted, M.ID as MemberID, M.FirstName, M.LastName
  FROM EventRoster ER
  JOIN Member M ON ER.Member = M.ID
  WHERE ER.Event = %s;
  """
  cursor.execute(roster_query, (event_id,))
  roster = cursor.fetchall()

  # For each member, get allergies
  for member in roster:
    member_id = member["MemberID"]
    allergies_query = """
    SELECT A.Name
    FROM Allergy A
    JOIN AllergyUsers AU ON A.ID = AU.AllergyID
    WHERE AU.UserID = %s;
    """
    cursor.execute(allergies_query, (member_id,))
    allergies = cursor.fetchall()
    allergies_list = [a["Name"] for a in allergies] if allergies else []
    member["Allergies"] = ", ".join(allergies_list)

  event_data = dict(event_row)
  event_data["Roster"] = roster

  return jsonify(event_data), 200


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
