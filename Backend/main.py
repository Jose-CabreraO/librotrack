from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from Backend.auth import validate_user, register_user
from Backend.models import create_tables
from Backend.db import init_db
from datetime import datetime
import sqlite3, os

# Inicializar base de datos y estructura
init_db()
create_tables()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="librotrack_key")

@app.get("/")
def root():
    return RedirectResponse("/index.html")

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    if validate_user(email, password):
        # Obtener el nombre del usuario desde la base de datos
        conn = sqlite3.connect("Backend/users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            request.session["usuario"] = row[0]  # GUARDA EL NOMBRE
        else:
            request.session["usuario"] = "Usuario"

        return RedirectResponse("/dashboard.html", status_code=302)
    return HTMLResponse("<h2 style='color:red;text-align:center;'>Usuario o contraseña incorrectos</h2>", status_code=401)

@app.post("/register")
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    success = register_user(name, email, password)
    if success:
        return RedirectResponse("/index.html", status_code=302)
    return HTMLResponse("<h2 style='color:red;text-align:center;'>Correo ya registrado</h2>", status_code=400)

@app.post("/add-product")
async def add_product(
    request: Request,
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    image: UploadFile = File(None)
):
    image_path = None
    if image:
        upload_dir = "Frontend/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        image_path = f"{upload_dir}/{image.filename}"
        with open(image_path, "wb") as f:
            f.write(await image.read())

    usuario = request.session.get("usuario", "desconocido")
    conn = sqlite3.connect("Backend/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, price, stock, image_path, created_by)
        VALUES (?, ?, ?, ?, ?)
    """, (name, price, stock, image_path, usuario))
    conn.commit()
    conn.close()
    return RedirectResponse("/dashboard.html", status_code=302)

@app.get("/products")
def get_products():
    conn = sqlite3.connect("Backend/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock, image_path FROM products")
    rows = cursor.fetchall()
    conn.close()
    products = [
        {"id": r[0], "name": r[1], "price": r[2], "stock": r[3], "image": r[4]}
        for r in rows
    ]
    return products

@app.post("/add-sale")
async def add_sale(
    request: Request,
    producto: str = Form(...),
    cliente: str = Form(...),
    cantidad: int = Form(...),
    empresa: str = Form(...),
    factura: str = Form(None)
):
    conn = sqlite3.connect("Backend/users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT stock FROM products WHERE name = ?", (producto,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return HTMLResponse("❌ Producto no encontrado", status_code=404)

    stock_actual = result[0]
    if cantidad > stock_actual:
        conn.close()
        return HTMLResponse("❌ Stock insuficiente", status_code=400)

    estado = "pagado" if factura else "pendiente"
    vendedor = request.session.get("usuario", "desconocido")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO sales (producto, cliente, cantidad, empresa, factura, estado, vendedor, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (producto, cliente, cantidad, empresa, factura, estado, vendedor, fecha))

    cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (cantidad, producto))

    conn.commit()
    conn.close()
    return RedirectResponse("/dashboard.html", status_code=302)

@app.get("/sales")
def get_sales():
    conn = sqlite3.connect("Backend/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.producto, s.cliente, s.cantidad, s.empresa, s.factura, s.estado, s.vendedor, s.fecha, p.price
        FROM sales s
        JOIN products p ON s.producto = p.name
        ORDER BY s.fecha DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "producto": r[0],
            "cliente": r[1],
            "cantidad": r[2],
            "empresa": r[3],
            "factura": r[4],
            "estado": r[5],
            "vendedor": r[6],
            "fecha": r[7],
            "total": r[8] * r[2]  # precio * cantidad
        }
        for r in rows
    ]


@app.get("/usuario-logueado")
def usuario_logueado(request: Request):
    return {"name": request.session.get("usuario", "Invitado")}

app.mount("/", StaticFiles(directory="Frontend", html=True), name="static")

print("💡 main.py cargado correctamente")
