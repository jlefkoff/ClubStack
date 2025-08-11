########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################
from backend.utils.db_utils import execute_query
from backend.db_connection import db
from flask import Blueprint, current_app, jsonify, make_response, request

# ------------------------------------------------------------
# Create a new Blueprint object, which is a collection of
# routes.
merch_bp = Blueprint("merch", __name__)


# ------------------------------------------------------------
# GET /merch-items - Browse available merch
@merch_bp.route("/", methods=["GET"])
def get_merch_items():
    # Stub: Return empty list or placeholder data
    query = """
   SELECT * FROM MerchItem;
   """
    return execute_query(query)


# ------------------------------------------------------------
# GET /merch-items/<id> - Get specific merch item
@merch_bp.route("/<int:item_id>", methods=["GET"])
def get_merch_item(item_id):
    query = f"""
    SELECT * FROM MerchItem WHERE ID = {item_id};
    """
    return execute_query(query)


# ------------------------------------------------------------
# POST /merch-items - Post new merch item
@merch_bp.route("/merch-items", methods=["POST"])
def post_merch_item():
    # Stub: Accept posted data and return success
    return jsonify({"message": "Merch item created (stub)"}), 201


# ------------------------------------------------------------
# POST /merch-sales - Record a merch sale
@merch_bp.route("/merch-sales", methods=["POST"])
def post_merch_sale():
    # Stub: Accept sale data and return success
    return jsonify({"message": "Merch sale recorded (stub)"}), 201


# ------------------------------------------------------------
# GET /merch-report - Merch sales report
@merch_bp.route("/merch-report", methods=["GET"])
def merch_report():
    # Stub: Return placeholder report
    return jsonify({"report": "Merch sales report (stub)"}), 200
