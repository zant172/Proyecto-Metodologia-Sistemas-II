from .database import get_connection
from PyQt6.QtWidgets import QMessageBox

def process_sale(cart_items, user_id, id_metodo_pago):
    conn = get_connection()
    if not conn: return False, "Error conexión BD."
    
    if not id_metodo_pago:
        return False, "Error: Debe seleccionar un método de pago."
        
    cursor = None
    try:
        cursor = conn.cursor()
        total_sale = sum(item['subtotal'] for item in cart_items)
        if total_sale <= 0: return False, "Carrito vacío o total cero."

        cursor.execute("BEGIN TRANSACTION")

        q_venta = "INSERT INTO Ventas (idUsuario, Total, idMetodoPago) OUTPUT INSERTED.idVenta VALUES (?, ?, ?)"
        cursor.execute(q_venta, (user_id, total_sale, id_metodo_pago))
        
        id_venta_row = cursor.fetchone()
        if not id_venta_row or not id_venta_row[0]:
            raise Exception("No se generó ID de Venta.")
        id_venta = id_venta_row[0]

        q_detalle = "INSERT INTO DetalleVentas (idVenta, idProducto, Cantidad, PrecioUnitario) VALUES (?, ?, ?, ?)"
        q_stock = "UPDATE Productos SET Stock = Stock - ? WHERE idProducto = ? AND Stock >= ?"

        detalles_data = []
        stock_data = []

        for item in cart_items:
            if not all(k in item for k in ['id', 'cantidad', 'precio']) or item['cantidad'] <= 0:
                 raise Exception(f"Item inválido en carrito: {item.get('nombre', 'Desconocido')}")
            
            # Re-verificación de stock dentro de la transacción
            stock_check = cursor.execute("SELECT Stock FROM Productos WHERE idProducto = ?", (item['id'],)).fetchone()
            if not stock_check or stock_check[0] < item['cantidad']:
                raise Exception(f"Stock insuficiente para '{item['nombre']}'. Disponible: {stock_check[0] if stock_check else 0}")

            detalles_data.append((id_venta, item['id'], item['cantidad'], item['precio']))
            stock_data.append((item['cantidad'], item['id'], item['cantidad']))

        cursor.executemany(q_detalle, detalles_data)
        cursor.executemany(q_stock, stock_data)
        
        conn.commit()
        return True, f"Venta #{id_venta} registrada."

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error procesando venta (ROLLBACK): {error_msg}")
        try:
            if conn: conn.rollback()
        except Exception as rb_e: print(f"⚠️ Error rollback: {rb_e}")

        return False, f"Error al procesar venta: {error_msg}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()