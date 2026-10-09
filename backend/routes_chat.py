from flask import Blueprint, request, jsonify
from database.db import get_db_connection

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/api/chat', methods=['GET'])
def get_chat_messages():
    """Fetches recent community chat history."""
    conn = get_db_connection()
    messages = conn.execute(
        """SELECT c.*, u.username 
           FROM chat_messages c 
           JOIN users u ON c.user_id = u.id 
           ORDER BY c.timestamp ASC LIMIT 100"""
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in messages]), 200

@chat_bp.route('/api/chat', methods=['POST'])
def post_chat_message():
    """Sends a new chat message."""
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')

    if not user_id or not content:
        return jsonify({"error": "Missing user_id or content"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO chat_messages (user_id, content) VALUES (?, ?)""",
        (user_id, content)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Message sent"}), 201