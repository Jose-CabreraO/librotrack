
import sqlite3
import hashlib

DB_PATH = "Backend/users.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_user(email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0] == hash_password(password)
    return False

def register_user(name: str, email: str, password: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
