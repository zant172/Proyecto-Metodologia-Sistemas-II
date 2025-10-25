from .database import get_connection

def process_sale(cart_items, user_id):
    conn = get_connection()
    if not conn: return False, "Error de conexión."
    try:
        cursor = conn.cursor()
        total_sale = sum(item['subtotal'] for item in cart_items)
        cursor.execute("BEGIN TRANSACTION")
        insert_venta_query = "INSERT INTO Ventas (idUsuario, Total) OUTPUT INSERTED.idVenta VALUES (?, ?)"
        cursor.execute(insert_venta_query, (user_id, total_sale))
        id_venta = cursor.fetchone()[0]
        if not id_venta: raise Exception("No se pudo crear Venta.")
        insert_detalle_query = "INSERT INTO DetalleVentas (idVenta, idProducto, Cantidad, PrecioUnitario) VALUES (?, ?, ?, ?)"
        update_stock_query = "UPDATE Productos SET Stock = Stock - ? WHERE idProducto = ?"
        detalles_data = [(id_venta, item['id'], item['cantidad'], item['precio']) for item in cart_items]
        stock_data = [(item['cantidad'], item['id']) for item in cart_items]
        cursor.executemany(insert_detalle_query, detalles_data)
        cursor.executemany(update_stock_query, stock_data)
        cursor.commit()
        return True, f"Venta #{id_venta} registrada."
    except Exception as e:
        cursor.rollback()
        print(f"❌ Error al procesar venta: {e}")
        return False, f"Error al procesar venta: {e}"
    finally:
        if conn: conn.close()