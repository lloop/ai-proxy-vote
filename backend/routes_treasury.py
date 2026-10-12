from flask import Blueprint, request, jsonify
from database.db import get_db_connection

treasury_bp = Blueprint('treasury_bp', __name__)

@treasury_bp.route('/api/treasury', methods=['GET'])
def get_treasury_logs():
    """Fetches all mock bank transactions across accounts, plus calculates the overall treasury balance."""
    conn = get_db_connection()
    
    logs = conn.execute(
        """SELECT t.*, b.account_name, b.account_number 
           FROM mock_bank_transactions t 
           JOIN mock_bank_accounts b ON t.account_id = b.id 
           ORDER BY t.created_at DESC"""
    ).fetchall()
    
    # Calculate total balance across all mock bank accounts
    balance = conn.execute(
        """SELECT COALESCE(SUM(balance), 0) as balance FROM mock_bank_accounts"""
    ).fetchone()
    
    conn.close()
    
    return jsonify({
        "balance": balance['balance'],
        "logs": [dict(row) for row in logs]
    }), 200

@treasury_bp.route('/api/treasury', methods=['POST'])
def log_treasury_transaction():
    """Logs a new deposit or withdrawal to a default or specified mock bank account. Restricted to organizers."""
    data = request.get_json()
    account_id = data.get('account_id')
    transaction_type = data.get('transaction_type') # 'deposit', 'withdrawal'
    amount = data.get('amount')
    logged_by = data.get('logged_by')
    description = data.get('description')

    if transaction_type not in ['deposit', 'withdrawal'] or not amount or not logged_by or not description:
        return jsonify({"error": "Invalid or missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user is an organizer
    user = cursor.execute("SELECT tier FROM users WHERE id = ?", (logged_by,)).fetchone()
    if not user or user['tier'] != 'organizer':
        conn.close()
        return jsonify({"error": "Unauthorized: Only organizers can log treasury transactions"}), 403

    # If no specific account_id is provided, default to the first available mock bank account
    if not account_id:
        default_account = cursor.execute("SELECT id FROM mock_bank_accounts ORDER BY created_at ASC LIMIT 1").fetchone()
        if not default_account:
            conn.close()
            return jsonify({"error": "No mock bank accounts found. Please create an account first."}), 400
        account_id = default_account['id']

    # Adjust account balance calculation
    multiplier = 1 if transaction_type == 'deposit' else -1
    signed_amount = float(amount) * multiplier

    cursor.execute(
        """UPDATE mock_bank_accounts SET balance = balance + ? WHERE id = ?""",
        (signed_amount, account_id)
    )

    cursor.execute(
        """INSERT INTO mock_bank_transactions (account_id, amount, transaction_type, description) 
           VALUES (?, ?, ?, ?)""",
        (account_id, amount, transaction_type, description)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Treasury transaction logged successfully"}), 201

@treasury_bp.route('/api/treasury/accounts', methods=['GET'])
def get_mock_bank_accounts():
    """Fetches all mock bank accounts and their current balances."""
    conn = get_db_connection()
    accounts = conn.execute("SELECT * FROM mock_bank_accounts ORDER BY created_at DESC").fetchall()
    conn.close()
    
    return jsonify({
        "accounts": [dict(row) for row in accounts]
    }), 200

@treasury_bp.route('/api/treasury/accounts', methods=['POST'])
def create_mock_bank_account():
    """Creates a new mock bank account. Restricted to organizers."""
    data = request.get_json()
    account_name = data.get('account_name')
    account_number = data.get('account_number')
    initial_balance = data.get('balance', 0.00)
    currency = data.get('currency', 'USD')
    logged_by = data.get('logged_by')

    if not account_name or not account_number or not logged_by:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user is an organizer
    user = cursor.execute("SELECT tier FROM users WHERE id = ?", (logged_by,)).fetchone()
    if not user or user['tier'] != 'organizer':
        conn.close()
        return jsonify({"error": "Unauthorized: Only organizers can manage mock bank accounts"}), 403

    cursor.execute(
        """INSERT INTO mock_bank_accounts (account_name, account_number, balance, currency) 
           VALUES (?, ?, ?, ?)""",
        (account_name, account_number, initial_balance, currency)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Mock bank account created successfully"}), 201

@treasury_bp.route('/api/treasury/accounts/<int:account_id>/transactions', methods=['POST'])
def log_mock_bank_transaction(account_id):
    """Simulates a deposit or withdrawal against a mock bank account."""
    data = request.get_json()
    amount = data.get('amount')
    transaction_type = data.get('transaction_type') # 'deposit', 'withdrawal'
    description = data.get('description')
    logged_by = data.get('logged_by')

    if transaction_type not in ['deposit', 'withdrawal'] or not amount or not logged_by:
        return jsonify({"error": "Invalid or missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user is an organizer
    user = cursor.execute("SELECT tier FROM users WHERE id = ?", (logged_by,)).fetchone()
    if not user or user['tier'] != 'organizer':
        conn.close()
        return jsonify({"error": "Unauthorized: Only organizers can execute mock transactions"}), 403

    # Adjust account balance calculation
    multiplier = 1 if transaction_type == 'deposit' else -1
    signed_amount = float(amount) * multiplier

    cursor.execute(
        """UPDATE mock_bank_accounts SET balance = balance + ? WHERE id = ?""",
        (signed_amount, account_id)
    )
    
    cursor.execute(
        """INSERT INTO mock_bank_transactions (account_id, amount, transaction_type, description) 
           VALUES (?, ?, ?, ?)""",
        (account_id, amount, transaction_type, description)
    )
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Mock bank transaction completed successfully"}), 201
