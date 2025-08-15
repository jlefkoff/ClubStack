########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################
from backend.utils.db_utils import execute_query, execute_update
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
# DELETE /<id> - Remove specific item
@merch_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_merch_item(item_id):
    query = """
    DELETE FROM MerchItem WHERE ID = %s;
    """
    return execute_update(query, (item_id))


# ------------------------------------------------------------
# POST /merch-items - Post new merch item
@merch_bp.route("/merch-items", methods=["POST"])
def post_merch_item():
    data = request.json
    query = """
    INSERT INTO MerchItem (Name, Price, Description, Quantity)
    VALUES (%s, %s, %s, %s);
    """
    params = (
        data["name"],
        data["price"],
        data["description"],
        data["quantity"],
    )
    new_item = execute_update(query, params)
    return jsonify(new_item), 201


# ------------------------------------------------------------
# POST /merch-sales - Record a merch sale
@merch_bp.route("/merch-sales", methods=["POST"])
def post_merch_sale():
    data = request.json

    # 1. Insert into MerchSale (Cash, SaleDate auto)
    sale_id = execute_update(
        "INSERT INTO MerchSale (Cash) VALUES (%s);", (data["cash"],)
    )

    execute_update(
        "INSERT INTO MerchSaleItems (MerchItem, MerchSale) VALUES (%s, %s);",
        (data["ID"], sale_id),
    )

    return jsonify({"sale_id": sale_id, "status": "success"}), 200


# ------------------------------------------------------------
# DELETE /merch-sales/<id> - Remove merch sale
@merch_bp.route("/merch-sales/<int:sale_id>", methods=["DELETE"])
def delete_merch_sale(sale_id):
    query = """
    DELETE FROM MerchSale WHERE ID = %s;
    """
    return execute_update(query, (sale_id,))


# ------------------------------------------------------------
# GET /merch-report - Merch sales report with sale price
@merch_bp.route("/merch-report", methods=["GET"])
def merch_report():
    query = """
  SELECT 
    MerchSale.ID, 
    MerchSale.Cash, 
    MerchSale.SaleDate,
    GROUP_CONCAT(MerchItem.Name) AS ItemsSold,
    SUM(MerchItem.Price) AS TotalSalePrice
  FROM MerchSale
  JOIN MerchSaleItems ON MerchSale.ID = MerchSaleItems.MerchSale
  JOIN MerchItem ON MerchSaleItems.MerchItem = MerchItem.ID
  GROUP BY MerchSale.ID;
  """
    return execute_query(query)
