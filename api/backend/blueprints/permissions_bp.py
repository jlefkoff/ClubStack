from flask import Blueprint, jsonify, request

from backend.utils.db_utils import execute_query

permissions_bp = Blueprint("permissions", __name__)


# POST /permissions/<member_id> - Assign permissions
@permissions_bp.route("/<int:member_id>", methods=["POST"])
def assign_permissions(member_id):
    data = request.json
    if not data or "permissions" not in data:
      return jsonify({"error": "No permissions provided"}), 400

    permissions = data["permissions"]
    if not isinstance(permissions, list) or not permissions:
      return jsonify({"error": "Permissions must be a non-empty list"}), 400

    # Prepare SQL for inserting permissions
    values = ", ".join(
      f"({member_id}, {permission_id})" for permission_id in permissions
    )
    query = f"""
    INSERT INTO MemberPermissions (Member, Permission)
    VALUES {values}
    ON CONFLICT DO NOTHING;
    """

    execute_query(query)
    return jsonify({"message": "Permissions assigned successfully"}), 201


# GET /permissions/<member_id> - Get permissions of member
@permissions_bp.route("/<int:member_id>", methods=["GET"])
def get_member_permissions(member_id):
    query = f"""
    SELECT M.FirstName, M.LastName, P.Title FROM Permission P JOIN MemberPermissions MP ON P.ID = MP.Permission
    JOIN Member M ON MP.Member = M.ID WHERE M.ID = {member_id};
    """
    return execute_query(query)


# POST /permissions - Create permission and assign accessible pages
@permissions_bp.route("/", methods=["POST"])
def create_permission():
  data = request.json
  if not data or "title" not in data:
    return jsonify({"error": "Title is required"}), 400

  title = data["title"]
  if not isinstance(title, str) or not title.strip():
    return jsonify({"error": "Title must be a non-empty string"}), 400

  # Insert permission
  query = """
  INSERT INTO Permission (Title) VALUES (%s)
  ON CONFLICT DO NOTHING;
  """
  params = (title.strip(),)
  execute_query(query, params)

  # Get permission ID
  get_id_query = "SELECT ID FROM Permission WHERE Title = %s;"
  result = execute_query(get_id_query, params)
  if not result or not result[0].get("ID"):
    return jsonify({"error": "Failed to create permission"}), 500
  permission_id = result[0]["ID"]

  # Assign pages if provided
  pages = data.get("pages")
  if pages and isinstance(pages, list):
    # Get page IDs from slugs
    page_ids = []
    for slug in pages:
      page_query = "SELECT ID FROM Page WHERE Slug = %s;"
      page_result = execute_query(page_query, (slug,))
      if page_result and page_result[0].get("ID"):
        page_ids.append(page_result[0]["ID"])
    if page_ids:
      values = ", ".join(f"({page_id}, {permission_id})" for page_id in page_ids)
      assign_query = f"""
      INSERT INTO PagePermissions (PageID, PermissionID)
      VALUES {values}
      ON CONFLICT DO NOTHING;
      """
      execute_query(assign_query)

  return jsonify({"message": "Permission created successfully"}), 201


# GET /permissions - List all permissions
@permissions_bp.route("/", methods=["GET"])
def list_permissions():
    query = """
    SELECT * FROM Permission;
    """
    return execute_query(query)

# DELETE /permissions/<int:permission_id> - Delete a permission
@permissions_bp.route("/<int:permission_id>", methods=["DELETE"])
def delete_permission(permission_id):
    query = """
    DELETE FROM Permission WHERE ID = %s;
    """
    execute_query(query, (permission_id,))
    return jsonify({"message": "Permission deleted successfully"}), 200

