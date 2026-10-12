from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from database.db import get_db_connection

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/members', methods=['GET'])
def get_users():
    search_query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_query:
        cursor.execute("""
            SELECT id, username as name, email, role, status, eligible_to_vote as eligible, created_at as joined 
            FROM users 
            WHERE username LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
        """, (f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("""
            SELECT id, username as name, email, role, status, eligible_to_vote as eligible, created_at as joined 
            FROM users 
            ORDER BY created_at DESC
        """)
    
    raw_members = cursor.fetchall()
    
    # Generate initials for each member dynamically
    members = []
    for m in raw_members:
        member_dict = dict(m)
        name_parts = member_dict['name'].split()
        if len(name_parts) >= 2:
            member_dict['initials'] = (name_parts[0][0] + name_parts[1][0]).upper()
        elif len(name_parts) == 1:
            member_dict['initials'] = name_parts[0][:2].upper()
        else:
            member_dict['initials'] = 'M'
        members.append(member_dict)

    # Fetch dynamic stats
    cursor.execute("SELECT COUNT(*) FROM users")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'Active'")
    active_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'Invited'")
    pending_invites = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE eligible_to_vote = 1")
    eligible_voters = cursor.fetchone()[0]
    
    conn.close()

    return render_template('members.html', 
                           members=members, 
                           total_members=total_members,
                           active_members=active_members,
                           pending_invites=pending_invites,
                           eligible_voters=eligible_voters)

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    """Registers a new community member."""
    data = request.get_json()
    username = data.get('username')
    contact_info = data.get('contact_info')
    tier = data.get('tier', 'general')

    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    import os
    print("Database path:", os.path.abspath("sound_system.sqlite3"))

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

@users_bp.route('/members/invite', methods=['POST'])
def invite_member():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_bp.login'))

    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role', 'member')

    if name and email:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, role, status, eligible_to_vote) 
            VALUES (?, ?, ?, 'Invited', 0)
        """, (name, email, role))
        conn.commit()
        conn.close()

    return redirect(url_for('users_bp.get_users'))
