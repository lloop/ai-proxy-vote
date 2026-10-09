from flask import Blueprint, request, jsonify
from database.db import get_db_connection

proposals_bp = Blueprint('proposals_bp', __name__)

@proposals_bp.route('/api/proposals', methods=['GET'])
def get_proposals():
    """Fetches all community proposals."""
    conn = get_db_connection()
    proposals = conn.execute(
        """SELECT p.*, u.username as creator_name 
           FROM proposals p 
           JOIN users u ON p.creator_id = u.id 
           ORDER BY p.created_at DESC"""
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in proposals]), 200

@proposals_bp.route('/api/proposals', methods=['POST'])
def create_proposal():
    """Creates a new governance proposal or spending request."""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    creator_id = data.get('creator_id')
    closes_at = data.get('closes_at')

    if not all([title, description, creator_id, closes_at]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO proposals (title, description, creator_id, closes_at) 
           VALUES (?, ?, ?, ?)""",
        (title, description, creator_id, closes_at)
    )
    conn.commit()
    proposal_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Proposal created successfully", "id": proposal_id}), 201

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