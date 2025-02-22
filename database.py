# database.py
import sqlite3
from werkzeug.security import generate_password_hash #for password hashing
from logging_setup import setup_audit_logger

# Set up the audit logger
audit_logger = setup_audit_logger()

#Establish connection to SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db') #connect or create a database file
    conn.row_factory = sqlite3.Row #Dictionary-like access to rows
    return conn

# Initialize Database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    #Create 'users' table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL)''')
    conn.commit()
    # Create an admin user if one does not exist
    cursor.execute("SELECT * FROM users WHERE username=?", ('admin',))
    # If no admin user found, create one with the password 'admin' (hashed) and role 'admin'
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', generate_password_hash('admin'), 'admin'))
        conn.commit()
        audit_logger.info("Admin user created.")
    conn.close()