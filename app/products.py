from app.database import get_connection

def get_all_products():
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT p.idProducto, p.Codigo, p.NombreProducto, c.NombreCategoria, p.Precio, p.Stock
            FROM Productos p
            JOIN Categorias c ON p.idCategoria = c.idCategoria
            WHERE p.Activo = 1
            ORDER BY p.NombreProducto
        """
        cursor.execute(query)
        products = cursor.fetchall()
        return products
    except Exception as e:
        print(f"❌ Error al obtener los productos: {e}")
        return []
    finally:
        if conn:
            conn.close()