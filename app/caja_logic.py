from .database import get_connection
from datetime import datetime

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    if not conn:
        return None, "Error conexión BD."
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params if params else [])
        res = None
        if commit:
            conn.commit()
            res = True
        elif fetch_one:
            res = cursor.fetchone()
        elif fetch_all:
            res = cursor.fetchall()
        return res, None
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception as rb_e:
                print(f"⚠️ Error rollback: {rb_e}")
        print(f"❌ Error SQL ({query[:50]}...): {e}")
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

# ============================================================================
# FUNCIONES DE GESTIÓN DE CAJA
# ============================================================================

def get_caja_activa():
    """Obtiene la caja activa (Abierta o Pausada) del día actual"""
    today = datetime.now().strftime('%Y-%m-%d')
    q = """
        SELECT idCaja, FechaCaja, Turno, Estado, idUsuarioApertura, 
               FechaHoraApertura, idUsuarioCierre, FechaHoraCierre
        FROM Cajas 
        WHERE FechaCaja = ? AND Estado IN ('Abierta', 'Pausada')
        ORDER BY idCaja DESC
    """
    return _execute_query(q, (today,), fetch_one=True)

def abrir_caja(user_id, turno='General'):
    """Abre una nueva caja para el día actual"""
    # Verifica si ya hay una caja abierta o pausada hoy
    caja_activa, err = get_caja_activa()
    if err:
        return False, f"Error verificando caja activa: {err}"
    if caja_activa:
        return False, f"Ya existe una caja {caja_activa.Estado.lower()} para hoy (Turno: {caja_activa.Turno})"
    
    today = datetime.now().strftime('%Y-%m-%d')
    q = """
        INSERT INTO Cajas (FechaCaja, Turno, idUsuarioApertura, FechaHoraApertura, Estado)
        VALUES (?, ?, ?, GETDATE(), 'Abierta')
    """
    ok, err = _execute_query(q, (today, turno, user_id), commit=True)
    if ok:
        return True, f"Caja abierta exitosamente (Turno: {turno})"
    else:
        return False, f"Error al abrir caja: {err}"

def pausar_caja():
    """Pausa la caja activa (para recesos entre turnos)"""
    caja_activa, err = get_caja_activa()
    if err:
        return False, f"Error verificando caja: {err}"
    if not caja_activa:
        return False, "No hay caja abierta para pausar"
    if caja_activa.Estado != 'Abierta':
        return False, f"La caja está {caja_activa.Estado.lower()}, no se puede pausar"
    
    q = "UPDATE Cajas SET Estado = 'Pausada' WHERE idCaja = ?"
    ok, err = _execute_query(q, (caja_activa.idCaja,), commit=True)
    if ok:
        return True, "Caja pausada exitosamente"
    else:
        return False, f"Error al pausar caja: {err}"

def reanudar_caja():
    """Reanuda la caja pausada"""
    caja_activa, err = get_caja_activa()
    if err:
        return False, f"Error verificando caja: {err}"
    if not caja_activa:
        return False, "No hay caja para reanudar"
    if caja_activa.Estado != 'Pausada':
        return False, f"La caja está {caja_activa.Estado.lower()}, no se puede reanudar"
    
    q = "UPDATE Cajas SET Estado = 'Abierta' WHERE idCaja = ?"
    ok, err = _execute_query(q, (caja_activa.idCaja,), commit=True)
    if ok:
        return True, "Caja reanudada exitosamente"
    else:
        return False, f"Error al reanudar caja: {err}"

def cerrar_caja(user_id):
    """Cierra la caja activa y calcula los totales"""
    caja_activa, err = get_caja_activa()
    if err:
        return False, f"Error verificando caja: {err}"
    if not caja_activa:
        return False, "No hay caja abierta para cerrar"
    
    # Calcula totales de ventas de esta caja
    q_ventas = "SELECT ISNULL(SUM(Total), 0) FROM Ventas WHERE idCaja = ?"
    ventas_data, err_v = _execute_query(q_ventas, (caja_activa.idCaja,), fetch_one=True)
    if err_v:
        return False, f"Error calculando ventas: {err_v}"
    
    # Calcula gastos del día (NO por caja, sino por fecha)
    q_gastos = "SELECT ISNULL(SUM(Monto), 0) FROM Gastos WHERE CONVERT(date, FechaGasto) = ?"
    gastos_data, err_g = _execute_query(q_gastos, (caja_activa.FechaCaja,), fetch_one=True)
    if err_g:
        return False, f"Error calculando gastos: {err_g}"
    
    total_ventas = float(ventas_data[0]) if ventas_data else 0.0
    total_gastos = float(gastos_data[0]) if gastos_data else 0.0
    balance_neto = total_ventas - total_gastos
    
    # Cierra la caja
    q_cerrar = """
        UPDATE Cajas 
        SET Estado = 'Cerrada', 
            idUsuarioCierre = ?, 
            FechaHoraCierre = GETDATE(),
            TotalVentas = ?,
            TotalGastos = ?,
            BalanceNeto = ?
        WHERE idCaja = ?
    """
    ok, err = _execute_query(q_cerrar, (user_id, total_ventas, total_gastos, balance_neto, caja_activa.idCaja), commit=True)
    if ok:
        return True, f"Caja cerrada exitosamente. Balance: ${balance_neto:.2f}"
    else:
        return False, f"Error al cerrar caja: {err}"

def get_resumen_caja_activa():
    """Obtiene el resumen de ventas y gastos de la caja activa"""
    caja_activa, err = get_caja_activa()
    if err:
        return None, f"Error verificando caja: {err}"
    if not caja_activa:
        return None, "No hay caja abierta"
    
    # Ventas por método de pago de esta caja
    q_ventas = """
        SELECT mp.Nombre, SUM(v.Total) AS TotalPorMetodo 
        FROM Ventas v 
        JOIN MetodosPago mp ON v.idMetodoPago = mp.idMetodoPago 
        WHERE v.idCaja = ? 
        GROUP BY mp.Nombre
    """
    ventas_data, err_v = _execute_query(q_ventas, (caja_activa.idCaja,), fetch_all=True)
    
    # Gastos del día (todos los gastos de la fecha, no por caja)
    q_gastos = "SELECT ISNULL(SUM(Monto), 0) FROM Gastos WHERE CONVERT(date, FechaGasto) = ?"
    gastos_data, err_g = _execute_query(q_gastos, (caja_activa.FechaCaja,), fetch_one=True)
    
    if err_v or err_g:
        return None, f"Error obteniendo resumen: {err_v or err_g}"
    
    gastos_total = float(gastos_data[0]) if gastos_data and gastos_data[0] else 0.0
    ventas_desglose = ventas_data if ventas_data else []
    ventas_total = sum(float(v.TotalPorMetodo) for v in ventas_desglose) if ventas_desglose else 0.0
    balance = ventas_total - gastos_total
    
    return {
        "caja": caja_activa,
        "ventas_total": ventas_total,
        "gastos_total": gastos_total,
        "balance_neto": balance,
        "ventas_desglose": ventas_desglose
    }, None

def get_historial_cajas(limit=30):
    """Obtiene el historial de cajas cerradas"""
    q = f"""
        SELECT TOP {limit} 
            c.idCaja, c.FechaCaja, c.Turno, c.Estado,
            u1.NombreCompleto AS UsuarioApertura,
            u2.NombreCompleto AS UsuarioCierre,
            c.FechaHoraApertura, c.FechaHoraCierre,
            c.TotalVentas, c.TotalGastos, c.BalanceNeto
        FROM Cajas c
        LEFT JOIN Usuarios u1 ON c.idUsuarioApertura = u1.idUsuario
        LEFT JOIN Usuarios u2 ON c.idUsuarioCierre = u2.idUsuario
        WHERE c.Estado = 'Cerrada'
        ORDER BY c.FechaCaja DESC, c.idCaja DESC
    """
    return _execute_query(q, fetch_all=True)

def get_ventas_de_caja(id_caja):
    """Obtiene todas las ventas de una caja específica"""
    q = """
        SELECT v.idVenta, v.FechaVenta, u.NombreCompleto AS Usuario, 
               v.Total, mp.Nombre AS MetodoPago
        FROM Ventas v
        JOIN Usuarios u ON v.idUsuario = u.idUsuario
        LEFT JOIN MetodosPago mp ON v.idMetodoPago = mp.idMetodoPago
        WHERE v.idCaja = ?
        ORDER BY v.FechaVenta ASC
    """
    return _execute_query(q, (id_caja,), fetch_all=True)

def get_detalle_venta(id_venta):
    """Obtiene el detalle de productos de una venta"""
    q = """
        SELECT p.NombreProducto, dv.Cantidad, dv.PrecioUnitario,
               (dv.Cantidad * dv.PrecioUnitario) AS Subtotal
        FROM DetalleVentas dv
        JOIN Productos p ON dv.idProducto = p.idProducto
        WHERE dv.idVenta = ?
    """
    return _execute_query(q, (id_venta,), fetch_all=True)

def get_historial_cierres(limit=None):
    """Obtiene el historial de todos los cierres de caja registrados
    
    Retorna una tupla (cierres, error) donde cierres es una lista de tuplas:
    (FechaHoraCierre, NombreUsuario, TotalVentas, TotalGastos, BalanceNeto)
    """
    query = """
        SELECT 
            c.FechaHoraCierre,
            u.NombreUsuario,
            c.TotalVentas,
            c.TotalGastos,
            c.BalanceNeto
        FROM Cajas c
        LEFT JOIN Usuarios u ON c.idUsuarioCierre = u.idUsuario
        WHERE c.Estado = 'Cerrada' AND c.FechaHoraCierre IS NOT NULL
        ORDER BY c.FechaHoraCierre DESC
    """
    
    if limit:
        query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
    
    return _execute_query(query, (), fetch_all=True)

