from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_db_connection

uses_bp = Blueprint('uses_bp', __name__)

@uses_bp.route('/uses', methods=['GET', 'POST'])
def manage_uses():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        if not user_id:
            return redirect(url_for('auth_bp.login'))

        scheduled_date = request.form.get('scheduled_date')
        description = request.form.get('description')
        fee_amount = 50.00

        if scheduled_date and description:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO events (scheduled_date, description, organizer_id, fee_amount, fee_status) 
                   VALUES (?, ?, ?, ?, 'pending')""",
                (scheduled_date, description, user_id, fee_amount)
            )
            conn.commit()
            conn.close()

        return redirect(url_for('uses_bp.manage_uses'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT su.*, u.username as organizer_name 
        FROM events su 
        LEFT JOIN users u ON su.organizer_id = u.id 
        ORDER BY su.scheduled_date DESC
    """)
    uses = cursor.fetchall()
    conn.close()

    return render_template('events.html', uses=uses)