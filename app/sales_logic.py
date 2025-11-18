from .database import get_connection
from .caja_logic import get_caja_activa

def process_sale(cart_items, user_id, id_metodo_pago):
    # Primero verificamos que haya una caja abierta
    caja_activa, err_caja = get_caja_activa()
    
    if err_caja:
        return False, f"Error verificando caja: {err_caja}"
    if not caja_activa:
        return False, "No hay caja abierta. Por favor, abra una caja desde 'Caja Diaria' antes de registrar ventas."
    # caja_activa es una tupla: (idCaja, FechaCaja, Turno, Estado, idUsuarioApertura, FechaHoraApertura, idUsuarioCierre, FechaHoraCierre)
    if caja_activa[3] == 'Pausada':  # Estado es el índice 3
        return False, "La caja está pausada. Por favor, reanúdela desde 'Caja Diaria' antes de registrar ventas."
    
    # Validaciones de negocio
    if not cart_items:
        return False, "El carrito está vacío."
    
    if not id_metodo_pago:
        return False, "Debe seleccionar un método de pago."
    
    # Validar que todas las cantidades sean positivas
    for item in cart_items:
        if item['quantity'] <= 0:
            return False, f"La cantidad del producto '{item['name']}' debe ser mayor a cero."
        if item['subtotal'] < 0:
            return False, f"El subtotal del producto '{item['name']}' no puede ser negativo."
    
    conn = get_connection()
    if not conn:
        return False, "Error conexión BD."
    
    cursor = None
    try:
        cursor = conn.cursor()
        total_sale = sum(item['subtotal'] for item in cart_items)
        if total_sale <= 0:
            return False, "El total de la venta debe ser mayor a cero."

        # PyODBC con autocommit=False inicia transacción automáticamente al primer execute
        # Se confirma con conn.commit() o se deshace con conn.rollback()
        # IMPORTANTE: NO usar "BEGIN TRANSACTION" explícito ya que pyodbc lo maneja

        # Registra la venta vinculada a la caja activa
        # caja_activa[0] es idCaja
        q_venta = "INSERT INTO Ventas (idCaja, idUsuario, Total, idMetodoPago) OUTPUT INSERTED.idVenta VALUES (?, ?, ?, ?)"
        cursor.execute(q_venta, (caja_activa[0], user_id, total_sale, id_metodo_pago))
        
        id_venta_row = cursor.fetchone()
        if not id_venta_row or not id_venta_row[0]:
            raise Exception("No se generó ID de Venta.")
        id_venta = id_venta_row[0]

        q_detalle = "INSERT INTO DetalleVentas (idVenta, idProducto, Cantidad, PrecioUnitario) VALUES (?, ?, ?, ?)"
        q_stock = "UPDATE Productos SET Stock = Stock - ? WHERE idProducto = ? AND Stock >= ?"

        detalles_data = []
        stock_data = []

        for item in cart_items:
            # Los campos del carrito son: id, name, price, quantity, stock_max, subtotal
            if not all(k in item for k in ['id', 'quantity', 'price', 'name']) or item['quantity'] <= 0:
                 raise Exception(f"Item inválido en carrito: {item.get('name', 'Desconocido')}")
            
            # Re-verificación de stock dentro de la transacción para evitar race conditions
            cursor.execute("SELECT Stock FROM Productos WHERE idProducto = ?", (item['id'],))
            stock_check = cursor.fetchone()
            if not stock_check or stock_check[0] < item['quantity']:
                raise Exception(f"Stock insuficiente para '{item['name']}'. Disponible: {stock_check[0] if stock_check else 0}")

            detalles_data.append((id_venta, item['id'], item['quantity'], item['price']))
            stock_data.append((item['quantity'], item['id'], item['quantity']))

        cursor.executemany(q_detalle, detalles_data)
        cursor.executemany(q_stock, stock_data)
        
        conn.commit()
        return True, f"Venta #{id_venta} registrada."

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error procesando venta (ROLLBACK): {error_msg}")
        if conn:
            try:
                conn.rollback()
            except Exception as rb_e:
                print(f"⚠️ Error durante rollback: {rb_e}")
        return False, f"Error al procesar venta: {error_msg}"
    finally:
        # Cierra recursos en orden correcto y de forma segura
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