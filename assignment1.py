from flask import Flask, request, jsonify, session
import sqlite3
import uuid
import logging
from datetime import timedelta
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex  # Secure random secret key
app.permanent_session_lifetime = timedelta(minutes=30)

# Secure session cookies
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Username validation: 3-20 characters; allowed characters: letters, digits, underscore, hyphen, period
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_.-]{3,20}$')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize Database and create admin user if not exists
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

# Add HTTP security headers to every response
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def validate_input(username, password):
    if not username or not password:
        return "Username and password are required."
    if not USERNAME_REGEX.match(username):
        return "Invalid username. Must be 3-20 characters and contain only letters, numbers, underscores, hyphens, or dots."
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    return None

@app.route('/')
def hello_world():
    return 'Hello World'

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
        logging.info(f"User {username} registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        logging.warning(f"Registration failed: Username {username} already exists.")
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
        logging.info(f"User {username} logged in successfully.")
        return jsonify({'message': 'Login successful'}), 200
    else:
        logging.warning(f"Failed login attempt for username {username}.")
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/changepw', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not username or not old_password or not new_password:
        return jsonify({'error': 'Username, old password, and new password are required.'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user['password'], old_password):
        logging.warning(f"Failed password change attempt for username {username}.")
        conn.close()
        return jsonify({'error': 'Invalid username or password'}), 400

    cursor.execute("UPDATE users SET password=? WHERE username=?", (generate_password_hash(new_password), username))
    conn.commit()
    conn.close()
    logging.info(f"User {username} changed password successfully.")
    return jsonify({'message': 'Password changed successfully'}), 201

@app.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        logging.warning("Unauthorized access attempt to /admin.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as admin {session["username"]}'}), 200

@app.route('/user', methods=['GET'])
def user():
    if 'username' not in session:
        logging.warning("Unauthorized access attempt to /user.")
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as user {session["username"]}'}), 200

if __name__ == '__main__':
    # Running with an ad-hoc SSL context for HTTPS in development.
    app.run(ssl_context='adhoc')
