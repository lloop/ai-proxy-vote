from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from database.db import get_db_connection
from datetime import datetime, timedelta

proposals_bp = Blueprint('proposals_bp', __name__)

@proposals_bp.route('/proposals', methods=['GET', 'POST'])
def get_proposals():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth_bp.login'))

        title = request.form.get('title')
        description = request.form.get('body')  # Matches textarea name 'body'
        closes_at = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')

        if title and description:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO proposals (title, description, creator_id, closes_at) 
                   VALUES (?, ?, ?, ?)""",
                (title, description, user_id, closes_at)
            )
            conn.commit()
            conn.close()

        # Redirect back to the GET view so it renders the HTML page
        return redirect(url_for('proposals_bp.get_proposals'))

    # GET request: fetch proposals from DB and render the HTML template
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.username as creator_name 
        FROM proposals p 
        LEFT JOIN users u ON p.creator_id = u.id 
        ORDER BY p.created_at DESC
    """)
    proposals = cursor.fetchall()
    conn.close()

    return render_template('proposals.html', proposals=proposals)

@proposals_bp.route('/api/proposals', methods=['POST'])
def create_proposal():
    """Creates a new governance proposal or spending request."""
    # Enforce session-based user attribution instead of client payload
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    closes_at = data.get('closes_at')

    if not all([title, description, closes_at]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO proposals (title, description, creator_id, closes_at) 
           VALUES (?, ?, ?, ?)""",
        (title, description, user_id, closes_at)
    )
    conn.commit()
    proposal_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Proposal created successfully", "id": proposal_id}), 201

@proposals_bp.route('/proposals', methods=['POST'])
def submit_proposal_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_bp.login'))

    title = request.form.get('title')
    description = request.form.get('body') # Note: your textarea name is 'body'
    
    # Calculate or set a default closes_at date (e.g., 3 days from now)
    from datetime import datetime, timedelta
    closes_at = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')

    if title and description:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO proposals (title, description, creator_id, closes_at) 
               VALUES (?, ?, ?, ?)""",
            (title, description, user_id, closes_at)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('proposals_bp.get_proposals'))

@proposals_bp.route('/api/proposals/<int:proposal_id>/vote', methods=['POST'])
def cast_vote(proposal_id):
    """Casts a vote on a proposal using the user's current voting weight."""
    data = request.get_json()
    user_id = data.get('user_id')
    choice = data.get('choice') # 'yes', 'no', 'abstain'

    if choice not in ['yes', 'no', 'abstain']:
        return jsonify({"error": "Invalid vote choice"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user's current voting weight
    user = cursor.execute("SELECT voting_weight FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    weight = user['voting_weight']

    try:
        cursor.execute(
            """INSERT INTO votes (proposal_id, user_id, choice, weight_cast) 
               VALUES (?, ?, ?, ?)""",
            (proposal_id, user_id, choice, weight)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Vote recorded successfully", "weight_cast": weight}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "User has already voted on this proposal"}), 400

@proposals_bp.route('/api/proposals/<int:proposal_id>/veto', methods=['POST'])
def organizer_veto(proposal_id):
    """Allows an organizer to exercise a safety veto, rejecting the proposal."""
    data = request.get_json()
    user_id = data.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user is an organizer
    user = cursor.execute("SELECT tier FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or user['tier'] != 'organizer':
        conn.close()
        return jsonify({"error": "Unauthorized: Only organizers can apply a safety veto"}), 403

    cursor.execute(
        "UPDATE proposals SET status = 'rejected' WHERE id = ?",
        (proposal_id,)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Proposal rejected via organizer safety veto"}), 200