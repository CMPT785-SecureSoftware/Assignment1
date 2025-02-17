from flask import Flask, request, jsonify, session
import sqlite3
import hashlib
import uuid
import logging
from datetime import timedelta

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex  # Secure random secret key
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize Database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL)''')
    conn.commit()
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username=?", ('admin',))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin'), 'admin'))
        conn.commit()
    conn.close()

init_db()

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@app.route('/register', methods=['POST'])
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

@app.route('/login', methods=['POST'])
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

@app.route('/changepw', methods=['POST'])
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

@app.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as admin {session["username"]}'}), 200

@app.route('/user', methods=['GET'])
def user():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'message': f'Logged in as user {session["username"]}'}), 200

if __name__ == '__main__':
    app.run()
    # app.run(ssl_context='adhoc')  # Secure HTTPS connection
