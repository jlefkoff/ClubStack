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
    """Execute an INSERT/UPDATE/DELETE query and return success response with inserted id if available"""
    cursor = db.get_db().cursor()
    cursor.execute(query, params or ())
    db.get_db().commit()
    inserted_id = (
        cursor.lastrowid if query.strip().upper().startswith("INSERT") else None
    )
    response = {"message": "Operation successful"}
    if inserted_id is not None:
        response["id"] = inserted_id
    return jsonify(response), 200
