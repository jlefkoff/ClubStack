########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
merch_bp = Blueprint('merch', __name__)

#------------------------------------------------------------
# GET /merch-items - Browse available merch
@merch_bp.route('/merch-items', methods=['GET'])
def get_merch_items():
  # Stub: Return empty list or placeholder data
  return jsonify([]), 200

#------------------------------------------------------------
# GET /merch-items/<id> - Get specific merch item
@merch_bp.route('/merch-items/<int:item_id>', methods=['GET'])
def get_merch_item(item_id):
  # Stub: Return placeholder item
  return jsonify({'id': item_id, 'name': 'Stub Merch Item'}), 200

#------------------------------------------------------------
# POST /merch-items - Post new merch item
@merch_bp.route('/merch-items', methods=['POST'])
def post_merch_item():
  # Stub: Accept posted data and return success
  return jsonify({'message': 'Merch item created (stub)'}), 201

#------------------------------------------------------------
# POST /merch-sales - Record a merch sale
@merch_bp.route('/merch-sales', methods=['POST'])
def post_merch_sale():
  # Stub: Accept sale data and return success
  return jsonify({'message': 'Merch sale recorded (stub)'}), 201

#------------------------------------------------------------
# GET /merch-report - Merch sales report
@merch_bp.route('/merch-report', methods=['GET'])
def merch_report():
  # Stub: Return placeholder report
  return jsonify({'report': 'Merch sales report (stub)'}), 200
