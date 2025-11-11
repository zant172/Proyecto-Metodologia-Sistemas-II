from .database import get_connection

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
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
            result = True
        elif fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        return result, None
    
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

def get_all_products():
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
    query = "SELECT Codigo, NombreProducto, idCategoria, Precio, Stock FROM Productos WHERE idProducto = ?"
    product, error = _execute_query(query, (product_id,), fetch_one=True)
    return product, error

def get_all_categories():
    query = "SELECT idCategoria, NombreCategoria FROM Categorias ORDER BY NombreCategoria"
    categories, error = _execute_query(query, fetch_all=True)
    return categories, error

def create_product(codigo, nombre, cat_id, precio, stock):
    query = """
        INSERT INTO Productos (Codigo, NombreProducto, idCategoria, Precio, Stock, Activo) 
        VALUES (?, ?, ?, ?, ?, 1)
    """
    params = (codigo, nombre, cat_id, precio, stock)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto creado exitosamente."
    else:
        if 'UNIQUE KEY' in str(error):
            return False, f"El código '{codigo}' o nombre '{nombre}' ya existe."
        return False, f"Error al crear producto: {error}"

def update_product(product_id, codigo, nombre, cat_id, precio, stock):
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
        if 'UNIQUE KEY' in str(error):
            return False, f"El código '{codigo}' o nombre '{nombre}' ya existe."
        return False, f"Error al actualizar producto: {error}"

def delete_product(product_id):
    query = "UPDATE Productos SET Activo = 0 WHERE idProducto = ?"
    params = (product_id,)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto eliminado exitosamente."
    else:
        return False, f"Error al eliminar producto: {error}"

def search_products(search_term):
    # Búsqueda segura de productos por nombre o código
    query = """
        SELECT p.idProducto, p.Codigo, p.NombreProducto, p.Precio, p.Stock
        FROM Productos p
        WHERE p.Activo = 1 AND p.Stock > 0 AND
              (p.NombreProducto LIKE ? OR p.Codigo LIKE ?)
        ORDER BY p.NombreProducto
    """
    term = f"%{search_term}%"
    params = (term, term)
    products, error = _execute_query(query, params, fetch_all=True)
    return products, error