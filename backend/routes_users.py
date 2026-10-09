from flask import Blueprint, request, jsonify
from database.db import get_db_connection

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/api/users', methods=['GET'])
def get_users():
    """Fetches all registered community members."""
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY username ASC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in users]), 200

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    """Registers a new community member."""
    data = request.get_json()
    username = data.get('username')
    contact_info = data.get('contact_info')
    tier = data.get('tier', 'general')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO users (username, contact_info, tier) VALUES (?, ?, ?)""",
            (username, contact_info, tier)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "User registered successfully", "id": user_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username already exists"}, 400)

@users_bp.route('/api/participation', methods=['POST'])
def log_participation():
    """Logs participation hours and updates user voting weight. Organizer only."""
    data = request.get_json()
    logged_by = data.get('logged_by')
    user_id = data.get('user_id')
    hours = data.get('hours')
    description = data.get('description')

    if not all([logged_by, user_id, hours, description]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify organizer tier
    organizer = cursor.execute("SELECT tier FROM users WHERE id = ?", (logged_by,)).fetchone()
    if not organizer or organizer['tier'] != 'organizer':
        conn.close()
        return jsonify({"error": "Unauthorized: Only organizers can log participation"}), 403

    # Insert participation log
    cursor.execute(
        """INSERT INTO participation_logs (user_id, hours, description, logged_by) 
           VALUES (?, ?, ?, ?)""",
        (user_id, hours, description, logged_by)
    )

    # Automatically increase voting weight (e.g., 1 hour = +0.1 weight, or custom formula)
    cursor.execute(
        """UPDATE users SET voting_weight = voting_weight + (? * 0.1) WHERE id = ?""",
        (hours, user_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Participation logged and voting weight updated"}), 201