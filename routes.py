# routes.py
from flask import Blueprint, request, jsonify, session
import sqlite3
import logging
from database import get_db_connection, hash_password

bp = Blueprint('routes', __name__)

@bp.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hash_password(password), 'user'))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()

    if user:
        session.permanent = True
        session['username'] = username
        session['role'] = user['role']
        logging.info(f"User {username} logged in")
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/changepw', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(old_password)))
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Invalid username or password'}), 400

    cursor.execute("UPDATE users SET password=? WHERE username=?", (hash_password(new_password), username))
    conn.commit()
    conn.close()
    logging.info(f"User {username} changed password")
    return jsonify({'message': 'Password changed successfully'}), 201

@bp.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as admin {session["username"]}'}), 200

@bp.route('/user', methods=['GET'])
def user():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as user {session["username"]}'}), 200