# database.py
import sqlite3
import hashlib #for password hashing

#Establish connection to SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db') #connect or create a database file
    conn.row_factory = sqlite3.Row #Dictionary-like access to rows
    return conn

def hash_password(password):
    # Hash password using SHA256
    return hashlib.sha256(password.encode()).hexdigest()

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
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username=?", ('admin',))
    # If no admin user found, create one with the password 'admin' (hashed) and role 'admin'
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin'), 'admin'))
        conn.commit()
    conn.close()
