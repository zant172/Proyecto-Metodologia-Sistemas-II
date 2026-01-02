from .database import get_connection

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    if not conn:
        return None, "Error: No se pudo conectar a la base de datos."
    
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params if params else [])
        
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
        if conn:
            try:
                conn.rollback()
            except Exception as rb_e:
                print(f"⚠️ Error durante rollback: {rb_e}")
        print(f"❌ Error en la consulta: {e}")
        return None, str(e)
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"⚠️ Error cerrando cursor: {e}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"⚠️ Error cerrando conexión: {e}")

def get_all_products():
    query = """
        SELECT p.idProducto, p.Codigo, p.NombreProducto, c.NombreCategoria, p.Precio, p.Stock, p.CodigoBarra
        FROM Productos p
        JOIN Categorias c ON p.idCategoria = c.idCategoria
        WHERE p.Activo = 1
        ORDER BY p.NombreProducto
    """
    products, error = _execute_query(query, fetch_all=True)
    return products, error

def get_product_by_id(product_id):
    query = "SELECT Codigo, NombreProducto, idCategoria, Precio, Stock, CodigoBarra FROM Productos WHERE idProducto = ?"
    product, error = _execute_query(query, (product_id,), fetch_one=True)
    return product, error

def get_all_categories():
    query = "SELECT idCategoria, NombreCategoria FROM Categorias ORDER BY NombreCategoria"
    categories, error = _execute_query(query, fetch_all=True)
    return categories, error

def create_product(codigo, nombre, cat_id, precio, stock, codigo_barra=None):
    # Validaciones de negocio
    if not nombre:
        return False, "El nombre es obligatorio."
    
    # Si no hay código, generar uno automático
    if not codigo:
        import time
        import random
        codigo = f"AUTO-{int(time.time())}-{random.randint(1000, 9999)}"
    
    if precio < 0:
        return False, "El precio no puede ser negativo."
    if stock < 0:
        return False, "El stock no puede ser negativo."
    
    query = """
        INSERT INTO Productos (Codigo, NombreProducto, idCategoria, Precio, Stock, CodigoBarra, Activo) 
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """
    params = (codigo, nombre, cat_id, precio, stock, codigo_barra if codigo_barra else None)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto creado exitosamente."
    else:
        if 'UNIQUE KEY' in str(error) or 'UNIQUE' in str(error):
            return False, f"El código '{codigo}' o nombre '{nombre}' ya existe."
        return False, f"Error al crear producto: {error}"

def update_product(product_id, codigo, nombre, cat_id, precio, stock, codigo_barra=None):
    # Validaciones de negocio
    if not nombre:
        return False, "El código y nombre son obligatorios."
    if precio < 0:
        return False, "El precio no puede ser negativo."
    if stock < 0:
        return False, "El stock no puede ser negativo."
    
    query = """
        UPDATE Productos 
        SET Codigo = ?, NombreProducto = ?, idCategoria = ?, Precio = ?, Stock = ?, CodigoBarra = ?
        WHERE idProducto = ?
    """
    params = (codigo, nombre, cat_id, precio, stock, codigo_barra if codigo_barra else None, product_id)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        return True, "Producto actualizado exitosamente."
    else:
        if 'UNIQUE KEY' in str(error) or 'UNIQUE' in str(error):
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
    # Búsqueda segura de productos por nombre, código o código de barra
    query = """
        SELECT p.idProducto, p.Codigo, p.NombreProducto, p.Precio, p.Stock
        FROM Productos p
        WHERE p.Activo = 1 AND p.Stock > 0 AND
              (p.NombreProducto LIKE ? OR p.Codigo LIKE ? OR p.CodigoBarra = ?)
        ORDER BY p.NombreProducto
    """
    term = f"%{search_term}%"
    params = (term, term, search_term)  # Búsqueda exacta para código de barra
    products, error = _execute_query(query, params, fetch_all=True)
    return products, error