from .database import get_connection
from datetime import datetime

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    if not conn: return None, "Error conexión BD."
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params if params else [])
        res = None
        if commit: conn.commit(); res = True
        elif fetch_one: res = cursor.fetchone()
        elif fetch_all: res = cursor.fetchall()
        return res, None
    except Exception as e:
        try: conn.rollback()
        except Exception as rb_e: print(f"⚠️ Error rollback: {rb_e}")
        print(f"❌ Error SQL ({query[:50]}...): {e}"); return None, str(e)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_dashboard_metrics():
    today = datetime.now().strftime('%Y-%m-%d')
    first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    queries = {
        "ventas_mes": ("SELECT SUM(Total) FROM Ventas WHERE FechaVenta >= ?", (first_day,)),
        "gastos_mes": ("SELECT SUM(Monto) FROM Gastos WHERE FechaGasto >= ?", (first_day,)),
        "stock_bajo": ("SELECT COUNT(*) FROM Productos WHERE Stock <= 5 AND Activo = 1", ())
    }
    results = {}
    for key, (query, params) in queries.items():
        data, error = _execute_query(query, params, fetch_one=True)
        results[key] = data[0] if data and data[0] is not None else 0.0
    balance = results["ventas_mes"] - results["gastos_mes"]
    return {
        "ventas_mes": f"${results['ventas_mes']:.2f}",
        "gastos_mes": f"${results['gastos_mes']:.2f}",
        "balance_mes": f"${balance:.2f}",
        "stock_bajo": str(int(results['stock_bajo']))
    }

def get_chart_data():
    q = "SELECT TOP 7 CONVERT(date, FechaVenta) AS Dia, SUM(Total) AS TotalVentas FROM Ventas GROUP BY CONVERT(date, FechaVenta) ORDER BY Dia DESC"
    data, err = _execute_query(q, fetch_all=True)
    if err or not data: return [], []
    data.reverse()
    labels = [row.Dia.strftime('%d/%m') for row in data]
    values = [float(row.TotalVentas) for row in data]
    return labels, values

def get_reports_data(start_date, end_date):
    q = "SELECT v.idVenta, v.FechaVenta, u.NombreCompleto AS Usuario, v.Total, mp.Nombre AS MetodoPago FROM Ventas v JOIN Usuarios u ON v.idUsuario = u.idUsuario LEFT JOIN MetodosPago mp ON v.idMetodoPago = mp.idMetodoPago WHERE CONVERT(date, v.FechaVenta) BETWEEN ? AND ? ORDER BY v.FechaVenta DESC"
    return _execute_query(q, (start_date, end_date), fetch_all=True)

def get_recent_expenses():
    q = "SELECT TOP 5 idGasto, Descripcion, Monto, Categoria, FechaGasto FROM Gastos ORDER BY idGasto DESC"
    return _execute_query(q, fetch_all=True)

def create_expense(description, amount, category):
    q = "INSERT INTO Gastos (Descripcion, Monto, Categoria, FechaGasto) VALUES (?, ?, ?, ?)"
    params = (description, amount, category if category != 'Seleccionar categoría' else None, datetime.now().strftime('%Y-%m-%d'))
    ok, err = _execute_query(q, params, commit=True)
    if ok: return True, "Gasto creado."
    else: return False, f"Error al crear: {err or '?'}"

def get_metodos_pago_activos():
    q = "SELECT idMetodoPago, Nombre FROM MetodosPago WHERE Activo = 1 ORDER BY Nombre"
    return _execute_query(q, fetch_all=True)

def get_metodos_pago_crud():
    q = "SELECT idMetodoPago, Nombre, TipoMetodo, Activo FROM MetodosPago ORDER BY Nombre"
    return _execute_query(q, fetch_all=True)

def get_metodo_pago_by_id(id_metodo):
    q = "SELECT Nombre, TipoMetodo, Activo FROM MetodosPago WHERE idMetodoPago = ?"
    return _execute_query(q, (id_metodo,), fetch_one=True)

def create_metodo_pago(nombre, tipo):
    q = "INSERT INTO MetodosPago (Nombre, TipoMetodo, Activo) VALUES (?, ?, 1)"
    ok, err = _execute_query(q, (nombre, tipo), commit=True)
    if ok: return True, "Método de pago creado."
    else:
        if err and 'UNIQUE' in err: return False, f"El método '{nombre}' ya existe."
        return False, f"Error al crear: {err or '?'}"

def update_metodo_pago(id_metodo, nombre, tipo, activo):
    q = "UPDATE MetodosPago SET Nombre = ?, TipoMetodo = ?, Activo = ? WHERE idMetodoPago = ?"
    ok, err = _execute_query(q, (nombre, tipo, activo, id_metodo), commit=True)
    if ok: return True, "Método de pago actualizado."
    else:
        if err and 'UNIQUE' in err: return False, f"El método '{nombre}' ya existe."
        return False, f"Error al actualizar: {err or '?'}"

def get_resumen_dia_actual():
    today = datetime.now().strftime('%Y-%m-%d')
    q_ventas = "SELECT mp.Nombre, SUM(v.Total) AS TotalPorMetodo FROM Ventas v JOIN MetodosPago mp ON v.idMetodoPago = mp.idMetodoPago WHERE CONVERT(date, v.FechaVenta) = ? GROUP BY mp.Nombre"
    q_gastos = "SELECT SUM(Monto) FROM Gastos WHERE CONVERT(date, FechaGasto) = ?"
    
    ventas_data, err_v = _execute_query(q_ventas, (today,), fetch_all=True)
    gastos_data, err_g = _execute_query(q_gastos, (today,), fetch_one=True)
    
    if err_v or err_g: return None, f"Error ventas: {err_v}\nError gastos: {err_g}"
    
    gastos_total = gastos_data[0] if gastos_data and gastos_data[0] is not None else 0.0
    ventas_desglose = ventas_data if ventas_data else []
    ventas_total = sum(v.TotalPorMetodo for v in ventas_desglose)
    balance = ventas_total - gastos_total
    
    return {
        "ventas_total": ventas_total,
        "gastos_total": gastos_total,
        "balance_neto": balance,
        "ventas_desglose": ventas_desglose # Lista de (NombreMetodo, Total)
    }, None

def check_cierre_realizado_hoy():
    today = datetime.now().strftime('%Y-%m-%d')
    q = "SELECT COUNT(*) FROM CierresDeCaja WHERE FechaCierre = ?"
    res, err = _execute_query(q, (today,), fetch_one=True)
    if err: return True, f"Error verificando cierre: {err}" # Asumir cerrado si hay error
    if res and res[0] > 0: return True, "La caja de hoy ya fue cerrada."
    return False, "Caja abierta."

def get_historial_cierres():
    q = "SELECT TOP 100 c.FechaCierre, u.NombreCompleto, c.TotalVentas, c.TotalGastos, c.BalanceNeto FROM CierresDeCaja c JOIN Usuarios u ON c.idUsuarioCierre = u.idUsuario ORDER BY c.FechaCierre DESC"
    return _execute_query(q, fetch_all=True)

def perform_cierre_caja(user_id):
    is_cerrado, msg_cerrado = check_cierre_realizado_hoy()
    if is_cerrado: return False, msg_cerrado
    
    resumen, err_resumen = get_resumen_dia_actual()
    if err_resumen: return False, f"Error obteniendo resumen: {err_resumen}"
    
    conn = get_connection()
    if not conn: return False, "Error conexión BD."
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        
        q_cierre = "INSERT INTO CierresDeCaja (FechaCierre, TotalVentas, TotalGastos, BalanceNeto, idUsuarioCierre) OUTPUT INSERTED.idCierre VALUES (?, ?, ?, ?, ?)"
        params_cierre = (
            datetime.now().strftime('%Y-%m-%d'),
            resumen['ventas_total'],
            resumen['gastos_total'],
            resumen['balance_neto'],
            user_id
        )
        cursor.execute(q_cierre, params_cierre)
        id_cierre_row = cursor.fetchone()
        if not id_cierre_row: raise Exception("No se generó ID de Cierre.")
        id_cierre = id_cierre_row[0]
        
        if resumen['ventas_desglose']:
            q_detalle = "INSERT INTO CierresDeCajaDetalle (idCierre, idMetodoPago, Total) SELECT ?, mp.idMetodoPago, ? FROM MetodosPago mp WHERE mp.Nombre = ?"
            params_detalle = []
            for (nombre_metodo, total_metodo) in resumen['ventas_desglose']:
                params_detalle.append((id_cierre, total_metodo, nombre_metodo))
            
            cursor.executemany(q_detalle, params_detalle)

        conn.commit()
        return True, f"Cierre de caja #{id_cierre} realizado exitosamente."
        
    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ Error crítico procesando cierre: {e}")
        return False, f"Error al procesar cierre: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()