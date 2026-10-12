import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db_connection
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        # Simple password check (assuming plain text or hashed based on your DB setup)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('chat_bp.chat_page'))
        
        flash('Invalid username or password', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'general')
        
        print(f"DEBUG: Received form data -> Username: {username}, Password length: {len(password) if password else 0}")
        
        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('auth_bp.signup'))
            
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            print("DEBUG: Connected to database.")
            conn.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, role)
            )
            conn.commit()
            return redirect(url_for('auth_bp.login'))
        except sqlite3.IntegrityError as e:
            flash('Username already exists.')
            print(f">>> INTEGRITY ERROR CAUGHT: {e}")
            flash(f'Database error: {e}')
        finally:
            conn.close()
            
    return render_template('signup.html')