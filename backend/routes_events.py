from flask import Blueprint, render_template, session, redirect, url_for
from database.db import get_db_connection

events_bp = Blueprint('events_bp', __name__)

@events_bp.route('/events', methods=['GET'])
def index():
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM events ORDER BY scheduled_date DESC").fetchall()
    conn.close()
    return render_template('events.html', events=events, active_page='events')