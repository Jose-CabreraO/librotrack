import sqlite3

def init_db():
    conn = sqlite3.connect("Backend/users.db")
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    """)

    # Crear tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image_path TEXT,
            created_by TEXT
        );
    """)

    # Crear tabla de ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            cliente TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            empresa TEXT NOT NULL,
            factura TEXT,
            estado TEXT NOT NULL,
            vendedor TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
