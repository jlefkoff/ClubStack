from flask import jsonify, make_response
from backend.db_connection import db


def execute_query(query, params=None):
    """Execute a SELECT query and return JSON response"""
    cursor = db.get_db().cursor()
    cursor.execute(query, params or ())
    data = cursor.fetchall()
    response = make_response(jsonify(data))
    response.status_code = 200
    return response


def execute_update(query, params=None):
    """
    Execute an INSERT/UPDATE/DELETE query and return the inserted ID if available.
    Does NOT return a Flask Response — returns plain Python values for reuse.
    """
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()

    inserted_id = cursor.lastrowid if query.strip().upper().startswith("INSERT") else None
    return inserted_id
