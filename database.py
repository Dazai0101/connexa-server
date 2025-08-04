# connexa-server/database.py

import sqlite3
import hashlib
import os

def init_db(path: str):
    """Initialize the SQLite database with users table."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

def hash_password(password: str) -> str:
    """Return the SHA-256 hash of a password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(path: str, username: str, password: str) -> tuple:
    """Register a new user with hashed password."""
    try:
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           (username.lower(), hash_password(password)))
            conn.commit()
        return True, "✅ Account created successfully."
    except sqlite3.IntegrityError:
        return False, "⚠️ Username already taken."
    except Exception as e:
        return False, f"❌ Registration failed: {str(e)}"

def login_user(path: str, username: str, password: str) -> bool:
    """Validate login credentials."""
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ? AND password = ?",
                       (username.lower(), hash_password(password)))
        return cursor.fetchone() is not None
