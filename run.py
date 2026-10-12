import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from database.db import init_db, get_db_connection
from backend.routes_proposals import proposals_bp
from backend.routes_treasury import treasury_bp
from backend.routes_chat import chat_bp
from backend.routes_auth import auth_bp
from backend.routes_users import users_bp
from backend.routes_events import events_bp
from backend.routes_usage import uses_bp

# Explicitly load .env from the script's directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__, template_folder="client/templates", static_folder="client/static")
app.secret_key = os.environ.get("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*")

# Register all Blueprints
app.register_blueprint(proposals_bp)
app.register_blueprint(treasury_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(events_bp)
app.register_blueprint(uses_bp)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/proposals", methods=["GET"])
def proposals_page():
    return render_template("proposals.html")

@app.route("/treasury", methods=["GET"])
def treasury_page():
    return render_template("treasury.html")

@app.route('/chat')
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    return render_template('chat.html', user_id=session['user_id'], username=session['username'], role=session['role'])

@app.route("/members", methods=["GET"])
def members_page():
    return render_template("members.html")

@socketio.on('send_message')
def handle_socket_message(data):
    user_id = session.get('user_id')
    if not user_id:
        return  # Unauthorized

    content = data.get('content')
    if not content:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Save to DB using the verified user ID
    cursor.execute(
        'INSERT INTO chat_messages (user_id, content) VALUES (?, ?)',
        (user_id, content)
    )
    conn.commit()
    
    # Fetch username for the broadcast
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    username = user['username'] if user else 'Unknown'
    
    # Get timestamp
    cursor.execute('SELECT timestamp FROM chat_messages WHERE id = last_insert_rowid()')
    msg_row = cursor.fetchone()
    timestamp = msg_row['timestamp'] if msg_row else ''
    
    conn.close()

    # Broadcast to all connected clients instantly
    emit('new_message', {
        'username': username,
        'content': content,
        'timestamp': timestamp
    }, broadcast=True)
      

if __name__ == "__main__":
    # Ensure the database file and tables exist before starting the server
    db_path = os.path.join(os.path.dirname(__file__), "database", "sound_system.sqlite3")
    if not os.path.exists(db_path):
        print("Database not found. Initializing...")
        init_db()
        
    socketio.run(app, debug=True)
    
    app.run(debug=True, host="0.0.0.0", port=5000)
    
    
    
