from .database import get_connection

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    if not conn: return None, "Error de conexión."
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = None
        if commit: conn.commit(); result = True
        elif fetch_one: result = cursor.fetchone()
        elif fetch_all: result = cursor.fetchall()
        return result, None
    except Exception as e: return None, str(e)
    finally:
        if conn: conn.close()

def get_all_products():
    query = "SELECT p.idProducto, p.Codigo, p.NombreProducto, c.NombreCategoria, p.Precio, p.Stock FROM Productos p JOIN Categorias c ON p.idCategoria = c.idCategoria WHERE p.Activo = 1 ORDER BY p.NombreProducto"
    return _execute_query(query, fetch_all=True)

def get_product_by_id(product_id):
    query = "SELECT Codigo, NombreProducto, idCategoria, Precio, Stock FROM Productos WHERE idProducto = ?"
    return _execute_query(query, (product_id,), fetch_one=True)

def get_all_categories():
    query = "SELECT idCategoria, NombreCategoria FROM Categorias ORDER BY NombreCategoria"
    return _execute_query(query, fetch_all=True)

def create_product(codigo, nombre, cat_id, precio, stock):
    query = "INSERT INTO Productos (Codigo, NombreProducto, idCategoria, Precio, Stock, Activo) VALUES (?, ?, ?, ?, ?, 1)"
    success, error = _execute_query(query, (codigo, nombre, cat_id, precio, stock), commit=True)
    if success: return True, "Producto creado."
    msg = f"Código '{codigo}' o nombre '{nombre}' ya existe." if error and 'UNIQUE KEY' in error else f"Error al crear: {error}"
    return False, msg

def update_product(product_id, codigo, nombre, cat_id, precio, stock):
    query = "UPDATE Productos SET Codigo = ?, NombreProducto = ?, idCategoria = ?, Precio = ?, Stock = ? WHERE idProducto = ?"
    success, error = _execute_query(query, (codigo, nombre, cat_id, precio, stock, product_id), commit=True)
    if success: return True, "Producto actualizado."
    msg = f"Código '{codigo}' o nombre '{nombre}' ya existe." if error and 'UNIQUE KEY' in error else f"Error al actualizar: {error}"
    return False, msg

def delete_product(product_id):
    query = "UPDATE Productos SET Activo = 0 WHERE idProducto = ?"
    success, error = _execute_query(query, (product_id,), commit=True)
    return (True, "Producto eliminado.") if success else (False, f"Error al eliminar: {error}")

def search_products(search_term):
    query = "SELECT p.idProducto, p.Codigo, p.NombreProducto, p.Precio, p.Stock FROM Productos p WHERE p.Activo = 1 AND p.Stock > 0 AND (p.NombreProducto LIKE ? OR p.Codigo LIKE ?) ORDER BY p.NombreProducto"
    term = f"%{search_term}%"
    return _execute_query(query, (term, term), fetch_all=True)