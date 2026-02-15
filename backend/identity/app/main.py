import os
from functools import wraps

from flask import Flask, g, jsonify, request

from services import (
    assign_permission_to_role,
    create_department,
    create_permission,
    create_role,
    decode_access_token,
    delete_permission,
    delete_role,
    get_user,
    get_user_snapshot,
    init_db,
    is_root_admin_user,
    login_user,
    add_user_role,
    remove_permission_from_role,
    register_user,
    replace_role_permission,
    seed_identity_data,
    update_permission,
    update_role,
)

app = Flask(__name__)
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")


def _extract_bearer_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth[7:].strip()


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_bearer_token()
        if not token:
            return jsonify({"error": "Missing bearer token"}), 401
        decoded = decode_access_token(token)
        if not decoded["ok"]:
            return jsonify({"error": decoded["error"]}), decoded["status"]
        g.auth_user_id = decoded["data"].get("sub")
        return fn(*args, **kwargs)

    return wrapper


def _has_internal_token():
    header_value = request.headers.get("X-Internal-Token", "")
    return bool(INTERNAL_API_TOKEN) and header_value == INTERNAL_API_TOKEN

@app.route('/')
def home():
    return "Welcome to the Identity Service!"


@app.route("/users/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}
    required = ["name", "email", "password", "department_id"]
    missing = [k for k in required if not body.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    result = register_user(
        name=body["name"],
        email=body["email"],
        password=body["password"],
        department_id=body["department_id"],
    )
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/departments", methods=["POST"])
def create_department_route():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403

    body = request.get_json(silent=True) or {}
    name = body.get("name")
    if not name or not str(name).strip():
        return jsonify({"error": "name is required"}), 400

    result = create_department(name=str(name), description=body.get("description"))
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status

@app.route("/users/<user_id>/roles", methods=["POST"])
def assign_role(user_id):
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403

    body = request.get_json(silent=True) or {}
    role_id = body.get("role_id")
    role_name = body.get("role_name")
    if not role_id and not role_name:
        return jsonify({"error": "role_id or role_name is required"}), 400

    result = add_user_role(user_id=user_id, role_id=role_id, role_name=role_name)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status

@app.route("/auth/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    if not body.get("email") or not body.get("password"):
        return jsonify({"error": "email and password are required"}), 400

    result = login_user(email=body["email"], password=body["password"])
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/roles", methods=["POST"])
def create_role_route():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    if not body.get("name"):
        return jsonify({"error": "name is required"}), 400
    result = create_role(
        name=str(body["name"]),
        description=body.get("description"),
        level=body.get("level", 0),
        is_root_admin=body.get("is_root_admin", False),
        parent_role_id=body.get("parent_role_id"),
    )
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/roles/<role_id>", methods=["PATCH"])
def update_role_route(role_id):
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    result = update_role(role_id, body)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/roles/<role_id>", methods=["DELETE"])
def delete_role_route(role_id):
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    result = delete_role(role_id)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/permissions", methods=["POST"])
def create_permission_route():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    if not body.get("name") or not body.get("min_sensitivity"):
        return jsonify({"error": "name and min_sensitivity are required"}), 400
    result = create_permission(
        name=str(body["name"]),
        description=body.get("description"),
        min_sensitivity=str(body["min_sensitivity"]),
    )
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/permissions/<permission_id>", methods=["PATCH"])
def update_permission_route(permission_id):
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    result = update_permission(permission_id, body)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/permissions/<permission_id>", methods=["DELETE"])
def delete_permission_route(permission_id):
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    result = delete_permission(permission_id)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/role-permissions", methods=["POST"])
def assign_role_permission_route():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    if not body.get("role_id") or not body.get("permission_id"):
        return jsonify({"error": "role_id and permission_id are required"}), 400
    result = assign_permission_to_role(str(body["role_id"]), str(body["permission_id"]))
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/role-permissions", methods=["DELETE"])
def remove_role_permission_route():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    if not body.get("role_id") or not body.get("permission_id"):
        return jsonify({"error": "role_id and permission_id are required"}), 400
    result = remove_permission_from_role(str(body["role_id"]), str(body["permission_id"]))
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/role-permissions", methods=["PATCH"])
def replace_role_permission_route():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    body = request.get_json(silent=True) or {}
    required = ["role_id", "old_permission_id", "new_permission_id"]
    missing = [k for k in required if not body.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    result = replace_role_permission(
        str(body["role_id"]),
        str(body["old_permission_id"]),
        str(body["new_permission_id"]),
    )
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/users/<user_id>", methods=["GET"])
@auth_required
def user_detail(user_id):
    if g.auth_user_id != user_id:
        root_check = is_root_admin_user(g.auth_user_id)
        if not root_check["ok"] or not root_check["data"]:
            return jsonify({"error": "Forbidden"}), 403

    result = get_user(user_id)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/users/<user_id>/snapshot", methods=["GET"])
def user_snapshot(user_id):
    if not _has_internal_token():
        token = _extract_bearer_token()
        if not token:
            return jsonify({"error": "Missing bearer token or internal token"}), 401
        decoded = decode_access_token(token)
        if not decoded["ok"]:
            return jsonify({"error": decoded["error"]}), decoded["status"]

        auth_user_id = decoded["data"].get("sub")
        if auth_user_id != user_id:
            root_check = is_root_admin_user(auth_user_id)
            if not root_check["ok"] or not root_check["data"]:
                return jsonify({"error": "Forbidden"}), 403

    result = get_user_snapshot(user_id)
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status


@app.route("/admin/seed", methods=["POST"])
def seed_data():
    if not _has_internal_token():
        return jsonify({"error": "Forbidden"}), 403
    result = seed_identity_data()
    status = result["status"]
    return jsonify(result["data"] if result["ok"] else {"error": result["error"]}), status

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)
