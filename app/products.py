from .database import get_connection # <--- CORRECCIÓN AQUÍ

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    """Función auxiliar para manejar la lógica de la base de datos."""
    conn = get_connection()
    if not conn:
        return None, "Error: No se pudo conectar a la base de datos."
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = None
        if commit:
            conn.commit()
            result = True # Para operaciones de commit, devolvemos éxito
        elif fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        return result, None # (Datos, Error)
    
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

# --- FUNCIONES DE LECTURA (READ) ---

def get_all_products():
    """Obtiene todos los productos activos."""
    query = """
        SELECT p.idProducto, p.Codigo, p.NombreProducto, c.NombreCategoria, p.Precio, p.Stock
        FROM Productos p
        JOIN Categorias c ON p.idCategoria = c.idCategoria
        WHERE p.Activo = 1
        ORDER BY p.NombreProducto
    """
    products, error = _execute_query(query, fetch_all=True)
    return products, error

def get_product_by_id(product_id):
    """Obtiene un producto específico por su ID."""
    query = "SELECT Codigo, NombreProducto, idCategoria, Precio, Stock FROM Productos WHERE idProducto = ?"
    product, error = _execute_query(query, (product_id,), fetch_one=True)
    return product, error

def get_all_categories():
    """Obtiene todas las categorías."""
    query = "SELECT idCategoria, NombreCategoria FROM Categorias ORDER BY NombreCategoria"
    categories, error = _execute_query(query, fetch_all=True)
    return categories, error

# --- FUNCIONES DE ESCRITURA (CREATE, UPDATE, DELETE) ---

def create_product(codigo, nombre, cat_id, precio, stock):
    """Crea un nuevo producto en la base de datos."""
    query = """
        INSERT INTO Productos (Codigo, NombreProducto, idCategoria, Precio, Stock, Activo) 
        VALUES (?, ?, ?, ?, ?, 1)
    """
    params = (codigo, nombre, cat_id, precio, stock)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto creado exitosamente."
    else:
        return False, f"Error al crear producto: {error}"

def update_product(product_id, codigo, nombre, cat_id, precio, stock):
    """Actualiza un producto existente."""
    query = """
        UPDATE Productos 
        SET Codigo = ?, NombreProducto = ?, idCategoria = ?, Precio = ?, Stock = ?
        WHERE idProducto = ?
    """
    params = (codigo, nombre, cat_id, precio, stock, product_id)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto actualizado exitosamente."
    else:
        return False, f"Error al actualizar producto: {error}"

def delete_product(product_id):
    """Desactiva un producto (borrado lógico)."""
    query = "UPDATE Productos SET Activo = 0 WHERE idProducto = ?"
    params = (product_id,)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto eliminado exitosamente."
    else:
        return False, f"Error al eliminar producto: {error}"