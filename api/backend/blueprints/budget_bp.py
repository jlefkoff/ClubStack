from flask import Blueprint, request, jsonify

budget_bp = Blueprint('budget', __name__)

# GET /budget - Show all budgets
@budget_bp.route('/', methods=['GET'])
def show_budgets():
  return jsonify({'message': 'Show all budgets (stub)'}), 200

# POST /budget - Create new budget proposal
@budget_bp.route('/', methods=['POST'])
def create_budget():
  return jsonify({'message': 'Create new budget proposal (stub)'}), 201

# GET /budget/<id> - Get existing budget data
@budget_bp.route('/<int:id>', methods=['GET'])
def get_budget(id):
  return jsonify({'budget_id': id, 'data': 'Budget data (stub)'}), 200

# GET /budget/<id>/report - Budget + active member analysis
@budget_bp.route('/<int:id>/report', methods=['GET'])
def budget_report(id):
  return jsonify({'budget_id': id, 'report': 'Budget + active member analysis (stub)'}), 200

# PUT /budget/<id>/approve - Approve submitted budget
@budget_bp.route('/<int:id>/approve', methods=['PUT'])
def approve_budget(id):
  return jsonify({'budget_id': id, 'message': 'Budget approved (stub)'}), 200
