from flask import Blueprint, request, jsonify
from database.db import get_db_connection

treasury_bp = Blueprint('treasury_bp', __name__)

@treasury_bp.route('/api/treasury', methods=['GET'])
def get_treasury_logs():
    """Fetches all treasury contributions and expenses, plus calculates the current balance."""
    conn = get_db_connection()
    logs = conn.execute(
        """SELECT t.*, u.username as logged_by_name 
           FROM treasury_logs t 
           JOIN users u ON t.logged_by = u.id 
           ORDER BY t.timestamp DESC"""
    ).fetchall()
    
    # Calculate balance
    balance = conn.execute(
        """SELECT 
             COALESCE(SUM(CASE WHEN transaction_type = 'contribution' THEN amount ELSE 0 END), 0) -
             COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END), 0) as balance
           FROM treasury_logs"""
    ).fetchone()
    
    conn.close()
    
    return jsonify({
        "balance": balance['balance'],
        "logs": [dict(row) for row in logs]
    }), 200

@treasury_bp.route('/api/treasury', methods=['POST'])
def log_treasury_transaction():
    """Logs a new contribution or expense. Restricted to organizers."""
    data = request.get_json()
    transaction_type = data.get('transaction_type') # 'contribution', 'expense'
    amount = data.get('amount')
    logged_by = data.get('logged_by')
    description = data.get('description')

    if transaction_type not in ['contribution', 'expense'] or not amount or not logged_by or not description:
        return jsonify({"error": "Invalid or missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user is an organizer
    user = cursor.execute("SELECT tier FROM users WHERE id = ?", (logged_by,)).fetchone()
    if not user or user['tier'] != 'organizer':
        conn.close()
        return jsonify({"error": "Unauthorized: Only organizers can log treasury transactions"}), 403

    cursor.execute(
        """INSERT INTO treasury_logs (transaction_type, amount, logged_by, description) 
           VALUES (?, ?, ?, ?)""",
        (transaction_type, amount, logged_by, description)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Treasury transaction logged successfully"}), 201