# routes.py
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from validation import validate_input
from logging_setup import setup_audit_logger

audit_logger = setup_audit_logger()

bp = Blueprint('routes', __name__)

@bp.route('/')
def hello_world():
    return 'Welcome to CMPT785 Assignment 1!'

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Validate both username and password
    validation_error = validate_input(username, password, check_username=True)
    if validation_error:
        return jsonify({'error': validation_error}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, generate_password_hash(password), 'user'))
        conn.commit()
        audit_logger.info(f"User {username} registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        audit_logger.warning(f"Registration failed for {username}: {e}")
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session.permanent = True
        session['username'] = username
        session['role'] = user['role']
        audit_logger.info(f"User {username} logged in successfully.")
        return jsonify({'message': 'Login successful'}), 200
    else:
        audit_logger.warning(f"Failed login attempt for username {username}.")
        return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/changepw', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not username or not old_password or not new_password:
        return jsonify({'error': 'Username, old password, and new password are required.'}), 400

    # Validate new password (skip username format check)
    new_validation_error = validate_input(username, new_password, check_username=False)
    if new_validation_error:
        return jsonify({'error': new_validation_error}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user['password'], old_password):
        audit_logger.warning(f"Failed password change attempt for username {username}.")
        conn.close()
        return jsonify({'error': 'Invalid username or password'}), 400

    cursor.execute("UPDATE users SET password=? WHERE username=?", 
                   (generate_password_hash(new_password), username))
    conn.commit()
    conn.close()
    audit_logger.info(f"User {username} changed password successfully.")
    return jsonify({'message': 'Password changed successfully'}), 201

@bp.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        audit_logger.warning("Unauthorized access attempt to /admin.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as admin {session["username"]}'}), 200

@bp.route('/user', methods=['GET'])
def user():
    if 'username' not in session:
        audit_logger.warning("Unauthorized access attempt to /user.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as user {session["username"]}'}), 200