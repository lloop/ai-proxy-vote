from flask import Flask, jsonify, render_template
from database.db import init_db
from backend.routes_proposals import proposals_bp
from backend.routes_treasury import treasury_bp
from backend.routes_chat import chat_bp
from backend.routes_users import users_bp
import os

app = Flask(__name__, template_folder="client/templates", static_folder="client/static")

# Register all Blueprints
app.register_blueprint(proposals_bp)
app.register_blueprint(treasury_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(users_bp)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/proposals", methods=["GET"])
def proposals_page():
    return render_template("proposals.html")

@app.route("/treasury", methods=["GET"])
def treasury_page():
    return render_template("treasury.html")

@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template("chat.html")

@app.route("/members", methods=["GET"])
def members_page():
    return render_template("members.html")

if __name__ == "__main__":
    # Ensure the database file and tables exist before starting the server
    db_path = os.path.join(os.path.dirname(__file__), "database", "sound_system.sqlite3")
    if not os.path.exists(db_path):
        print("Database not found. Initializing...")
        init_db()
    
    app.run(debug=True, host="0.0.0.0", port=5000)