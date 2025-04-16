import sqlite3

def create_tables():
    conn = sqlite3.connect("Backend/users.db")
    cursor = conn.cursor()

    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image_path TEXT,
            created_by TEXT
        )
    """)

    # Tabla de ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            empresa TEXT NOT NULL,
            factura TEXT,
            estado TEXT NOT NULL,
            vendedor TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
