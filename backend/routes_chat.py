from flask import Blueprint, request, jsonify, render_template, session
from database.db import get_db_connection

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/chat', methods=['GET'])
def chat_page():  
    """Renders the main chat interface HTML template."""
    return render_template('chat.html') 

@chat_bp.route('/api/chat', methods=['GET'])
def get_chat_messages():
    """Fetches recent community chat history, optionally filtered by proposal_id."""
    proposal_id = request.args.get('proposal_id')
    conn = get_db_connection()
    
    if proposal_id:
        messages = conn.execute(
            """SELECT c.*, u.username 
               FROM chat_messages c 
               JOIN users u ON c.user_id = u.id 
               WHERE c.proposal_id = ?
               ORDER BY c.timestamp ASC LIMIT 100""",
            (proposal_id,)
        ).fetchall()
    else:
        messages = conn.execute(
            """SELECT c.*, u.username 
               FROM chat_messages c 
               JOIN users u ON c.user_id = u.id 
               WHERE c.proposal_id IS NULL
               ORDER BY c.timestamp ASC LIMIT 100"""
        ).fetchall()
        
    conn.close()
    return jsonify([dict(row) for row in messages]), 200

@chat_bp.route('/api/chat', methods=['POST'])
def post_chat_message():
    """Sends a new chat message."""
    
    user_id = session.get('user_id')
    print("DEBUG: Received POST request to /api/chat", session.get('user_id'))
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    content = data.get('content') if data else None

    if not content:
        return jsonify({"error": "Missing content"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO chat_messages (user_id, content) VALUES (?, ?)""",
        (user_id, content)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Message sent"}), 201