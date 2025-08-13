from flask import Blueprint, jsonify, request
from datetime import datetime
from backend.db_connection import db
from backend.utils.db_utils import execute_query, execute_update

communications_bp = Blueprint("communications", __name__)


# POST /communications - Send mass communication
@communications_bp.route("/", methods=["POST"])
def send_mass_communication():
    data = request.get_json()
    subject = data.get("subject")
    content = data.get("content")
    recipients = data.get("recipients")  # List of member IDs

    if not subject or not content or not recipients:
        return jsonify({"error": "Missing required fields"}), 400

    communication_id = execute_update("""
    INSERT INTO Communication (Subject, Content, DateSent)
    VALUES (%s, %s, %s);
    """, (subject, content, datetime.now())
    )

    for member_id in recipients:
        query = """
        INSERT INTO CommunicationRecipients (Communication, Member) VALUES (%s, %s)
        """
        execute_update(query, (communication_id, member_id))

    return jsonify({"message": "Mass communication sent", "id": communication_id}), 201


# GET /communications - View messages received (for a member)
@communications_bp.route("/<int:member_id>", methods=["GET"])
def view_messages_received(member_id):
    if not member_id:
        return jsonify({"error": "Missing member_id"}), 400

    cursor = db.get_db().cursor()
    cursor.execute(
        """
    SELECT c.ID, c.Subject, c.Content, c.DateSent
    FROM Communication c
    JOIN CommunicationRecipients cr ON c.ID = cr.Communication
    WHERE cr.Member = %s
    ORDER BY c.DateSent DESC
    """,
        (member_id,),
    )
    messages = cursor.fetchall()
    return jsonify({"messages": messages}), 200


# GET /communications/<id> - Get a specific communication
@communications_bp.route("/<int:communication_id>", methods=["GET"])
def get_communication(communication_id):

    cursor = db.get_db().cursor()
    cursor.execute(
        "SELECT ID, Subject, Content, DateSent FROM Communication WHERE ID = %s",
        (communication_id,),
    )
    communication = cursor.fetchone()
    if not communication:
        return jsonify({"error": "Communication not found"}), 404
    return jsonify(communication), 200


# DELETE /communications/<id> - Delete a communication
@communications_bp.route("/<int:communication_id>", methods=["DELETE"])
def delete_communication(communication_id):
    cursor = db.get_db().cursor()
    cursor.execute(
        "DELETE FROM CommunicationRecipients WHERE Communication = %s",
        (communication_id,),
    )
    cursor.execute("DELETE FROM Communication WHERE ID = %s", (communication_id,))
    db.commit()
    return jsonify({"message": "Communication deleted"}), 200
