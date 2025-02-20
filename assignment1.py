from flask import Flask, request, jsonify, session, make_response
import sqlite3
import uuid
import os
import re
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from logging.handlers import TimedRotatingFileHandler
import logging
from flask_talisman import Talisman

app = Flask(__name__)

# Use a secure random secret key
app.secret_key = uuid.uuid4().hex
app.permanent_session_lifetime = timedelta(minutes=30)

# Secure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ======================
# Setup Logging
# ======================

# Create directories for log files if they do not exist
os.makedirs('audit-logs', exist_ok=True)
os.makedirs('application-logs', exist_ok=True)

# Setup Audit Logger (for user-related events)
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
audit_handler = TimedRotatingFileHandler(
    'audit-logs/audit-log.txt', when='midnight', interval=1, backupCount=30
)

# Files will be rotated with a suffix like "-2025-02-18.txt"
audit_handler.suffix = "%Y-%m-%d.txt"
audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
audit_logger.addHandler(audit_handler)

# Setup Application Logger (for program errors, HTTP errors, etc.)
app_logger = logging.getLogger('application')
app_logger.setLevel(logging.INFO)
app_handler = TimedRotatingFileHandler(
    'application-logs/application-log.txt', when='midnight', interval=1, backupCount=30
)

# Files will be rotated with a suffix like "-2025-02-18.txt"
app_handler.suffix = "%Y-%m-%d.txt"
app_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
app_logger.addHandler(app_handler)

# ======================
# Validation Settings
# ======================

# Username validation: 3-20 characters; allowed: letters, digits, underscore, hyphen, period
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_.-]{6,20}$')

# Password validation: at least 8 characters with at least one uppercase letter,
# one lowercase letter, one digit, and one special character.
def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    return re.fullmatch(pattern, password) is not None

def validate_input(username, password):
    if not username or not password:
        return "Username and password are required."
    if not USERNAME_REGEX.match(username):
        return ("Invalid username. Must be 3-20 characters and contain only letters, numbers, underscores, "
                "hyphens, or dots.")
    if not is_valid_password(password):
        return ("Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, "
                "one digit, and one special character.")
    if username.lower() in password.lower():
        return "Password should not contain the username."
    return None

# ======================
# Database Setup
# ======================

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL)''')
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE username=?", ('admin',))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', generate_password_hash('admin'), 'admin'))
        conn.commit()
    conn.close()

init_db()

# ======================
# HTTP Security Headers
# ======================

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-store'
    return response

# ======================
# Endpoints
# ======================

@app.route('/')
def hello_world():
    return 'Welcome to CMPT785 Assignment 1!'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    validation_error = validate_input(username, password)
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
    except sqlite3.IntegrityError:
        audit_logger.warning(f"Registration failed: Username {username} already exists.")
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
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

@app.route('/changepw', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not username or not old_password or not new_password:
        return jsonify({'error': 'Username, old password, and new password are required.'}), 400

    # Validate the new password using the same validation rules as for registration.
    # This check includes ensuring the password does not contain the username.
    new_validation_error = validate_input(username, new_password)
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

@app.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        audit_logger.warning("Unauthorized access attempt to /admin.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as admin {session["username"]}'}), 200

@app.route('/user', methods=['GET'])
def user():
    if 'username' not in session:
        audit_logger.warning("Unauthorized access attempt to /user.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as user {session["username"]}'}), 200

# ======================
# Error Handlers (Optional)
# ======================

@app.errorhandler(500)
def internal_error(error):
    app_logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found_error(error):
    app_logger.warning(f"404 error: {error}")
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    # Running with Flask-Talisman for HTTPS in production.
    Talisman(app, force_https=True)
    # Running with an ad-hoc SSL context for HTTPS in development.
    app.run(debug=True, ssl_context='adhoc')