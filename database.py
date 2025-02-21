# database.py
import sqlite3
from werkzeug.security import generate_password_hash
from logging_setup import setup_audit_logger

audit_logger = setup_audit_logger()

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
    # Create an admin user if one does not exist
    cursor.execute("SELECT * FROM users WHERE username=?", ('admin',))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', generate_password_hash('admin'), 'admin'))
        conn.commit()
        audit_logger.info("Admin user created.")
    conn.close()