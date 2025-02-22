# routes.py
# This module defines the primary routes for user authentication and role-based access within
# a Flask application. It includes user registration, login, password change, and role-specific
# endpoints for admin and regular users.

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from validation import validate_input
from logging_setup import setup_audit_logger

audit_logger = setup_audit_logger()

bp = Blueprint('routes', __name__)

@bp.route('/')
def hello_world():
    """
    Simple endpoint to verify that the application is running.
    """
    return 'Welcome to CMPT785 Assignment 1!'

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user. Expects JSON with 'username' and 'password'.
    Validates input, hashes the password, stores the new user in the database,
    and logs an audit message.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Validate username and password format
    validation_error = validate_input(username, password, check_username=True)
    if validation_error:
        return jsonify({'error': validation_error}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Attempt to insert the new user with a secure hash of their password
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, generate_password_hash(password), 'user'))
        conn.commit()
        audit_logger.info(f"User {username} registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        # Handle case where the username might already exist or other DB errors
        audit_logger.warning(f"Registration failed for {username}: {e}")
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        # Ensure database connection is closed regardless of success or failure
        conn.close()

@bp.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user. Expects JSON with 'username' and 'password'.
    Verifies the provided credentials and sets session data if valid.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if required fields are provided
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    # Retrieve the user record from the database
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    # Check the stored hashed password against the provided password
    if user and check_password_hash(user['password'], password):
        # Set session to track user login; used for role-based access
        session.permanent = True
        session['username'] = username
        session['role'] = user['role']
        audit_logger.info(f"User {username} logged in successfully.")
        return jsonify({'message': 'Login successful'}), 200
    else:
        # Log failed attempts for audit and security monitoring
        audit_logger.warning(f"Failed login attempt for username {username}.")
        return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/changepw', methods=['POST'])
def change_password():
    """
    Change an existing user's password. Expects JSON with 'username', 'old_password', and 'new_password'.
    Validates the new password, checks old password correctness, and updates the user record.
    """
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    # Ensure the required fields are provided
    if not username or not old_password or not new_password:
        return jsonify({'error': 'Username, old password, and new password are required.'}), 400

    # Validate new password format (username format check is skipped here)
    new_validation_error = validate_input(username, new_password, check_username=False)
    if new_validation_error:
        return jsonify({'error': new_validation_error}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    # Check if the user exists and if the old password is correct
    if not user or not check_password_hash(user['password'], old_password):
        audit_logger.warning(f"Failed password change attempt for username {username}.")
        conn.close()
        return jsonify({'error': 'Invalid username or password'}), 400

    # If validation passes, update the password with a new hashed value
    cursor.execute("UPDATE users SET password=? WHERE username=?", 
                   (generate_password_hash(new_password), username))
    conn.commit()
    conn.close()

    audit_logger.info(f"User {username} changed password successfully.")
    return jsonify({'message': 'Password changed successfully'}), 201

@bp.route('/admin', methods=['GET'])
def admin():
    """
    Admin-only endpoint. Checks session for 'role' == 'admin' before granting access.
    Returns a message indicating the logged-in admin user if authorized.
    """
    if 'username' not in session or session.get('role') != 'admin':
        audit_logger.warning("Unauthorized access attempt to /admin.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as admin {session["username"]}'}), 200

@bp.route('/user', methods=['GET'])
def user():
    """
    User-only endpoint. Requires any logged-in user. Returns a message indicating
    the currently logged-in user if authorized.
    """
    if 'username' not in session or session.get('role') != 'user':
        audit_logger.warning("Unauthorized access attempt to /user.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as user {session["username"]}'}), 200
