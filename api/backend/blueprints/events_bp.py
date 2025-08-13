from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query, execute_update
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
    data = request.get_json()
    print(data)
    required_fields = [
        "Author",
        "PartySize",
        "MaxSize",
        "EventLoc",
        "Randomized",
        "Name",
        "Description",
        "MeetLoc",
        "LeadOrg",
        "EventType",
        "RecItems",    
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    query = """
  INSERT INTO Event (
    Author, PartySize, MaxSize, EventLoc, Randomized,
    Name, Description, MeetLoc, LeadOrg, EventType, RecItems
  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
  """
    values = (
        data["Author"],
        data["PartySize"],
        data["MaxSize"],
        data["EventLoc"],
        data["Randomized"],
        data["Name"],
        data["Description"],
        data["MeetLoc"],
        data["LeadOrg"],
        data["EventType"],
        data["RecItems"]
    )
    try:
      id = execute_update(query, values)

      print(f"Event created with ID: {id}")
      return jsonify({"message": "Event created", "event_id": id}), 201
    except Exception as e:
      db.get_db().rollback()
      print(f"Error creating event: {e}")
      return jsonify({"error": "Failed to create event", "details": str(e)}), 500


# PUT /events/<id> - Update event
@events_bp.route("/<int:event_id>", methods=["PUT"])
def put_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Prepare the update query
    set_clause = ", ".join(f"{key} = %s" for key in data.keys())
    query = f"UPDATE Event SET {set_clause} WHERE ID = %s"
    values = tuple(data.values()) + (event_id,)

    cursor = db.get_db().cursor()
    cursor.execute(query, values)
    db.get_db().commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Event not found"}), 404

    return jsonify({"message": "Event updated successfully"}), 200

# DELETE /events/<id> - Delete event
@events_bp.route("/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    query = "DELETE FROM Event WHERE ID = %s"
    execute_update(query, (event_id,))
    return jsonify({"message": "Event deleted successfully"}), 200


# GET /events/<id>/roster - Get event roster
@events_bp.route("/<int:event_id>/roster", methods=["GET"])
def get_event_roster(event_id):
    cursor = db.get_db().cursor()
    query = """
    SELECT M.ID as MemberID, M.FirstName, M.LastName
    FROM EventRoster ER
    JOIN Member M ON ER.Member = M.ID
    WHERE ER.Event = %s;
    """
    cursor.execute(query, (event_id,))
    roster = cursor.fetchall()
    return jsonify({"event_id": event_id, "roster": roster}), 200

# GET /events/<id>/rsvp - Get event rsvps
@events_bp.route("/<int:event_id>/rsvp", methods=["GET"])
def get_event_rsvp(event_id):
  cursor = db.get_db().cursor()
  query = """
  SELECT ID, Event, CanBringCar, AvailStart, AvailEnd
  FROM RSVP
  WHERE Event = %s;
  """
  cursor.execute(query, (event_id,))
  rsvps = cursor.fetchall()
  return jsonify({"event_id": event_id, "rsvps": rsvps}), 200

# GET /events/report - Events report
@events_bp.route("/report", methods=["GET"])
def events_report():
    query = """
      SELECT
        e.Name as EventName,
        e.EventType,
        e.EventLoc,
        er.DateRegistered,
        er.Waitlisted,
        CASE
            WHEN er.Waitlisted = TRUE THEN 'Waitlisted'
            ELSE 'Confirmed'
        END as RegistrationStatus
      FROM EventRoster er
      JOIN Event e ON er.Event = e.ID
      WHERE er.Member = 3
      ORDER BY er.DateRegistered DESC;
    """
    return execute_query(query) 

# POST /rsvp - RSVP to an event
@events_bp.route("/rsvp", methods=["POST"])
def post_rsvp():
    data = request.get_json()
    if not data or "event_id" not in data or "member_id" not in data:
        return jsonify({"error": "Invalid data"}), 400

    event_id = data["event_id"]
    member_id = data["member_id"] # TODO: Use member id - need to add to schema
    can_bring_car = data.get("can_bring_car", False)
    avail_start = data.get("avail_start")
    avail_end = data.get("avail_end")

    query = """
    INSERT INTO RSVP (Event, CanBringCar, AvailStart, AvailEnd)
    VALUES (%s, %s, %s, %s);
    """
    params = (event_id, can_bring_car, avail_start, avail_end)

    cursor = db.get_db().cursor()
    cursor.execute(query, params)
    db.get_db().commit()

    return jsonify({"message": "RSVP created successfully"}), 201
