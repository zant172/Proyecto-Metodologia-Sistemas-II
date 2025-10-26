from .database import get_connection
from datetime import datetime

def _execute_query(query, params=(), fetch_one=False, fetch_all=False):
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
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        return result, None
    
    except Exception as e:
        print(f"❌ Error en la consulta del dashboard: {e}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

def get_dashboard_metrics():
    
    today = datetime.now().strftime('%Y-%m-%d')
    first_day_of_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')

    queries = {
        "ventas_mes": "SELECT SUM(Total) FROM Ventas WHERE FechaVenta >= ?",
        "gastos_mes": "SELECT SUM(Monto) FROM Gastos WHERE FechaGasto >= ?",
        "ventas_hoy": "SELECT SUM(Total) FROM Ventas WHERE CONVERT(date, FechaVenta) = ?",
        "stock_bajo": "SELECT COUNT(*) FROM Productos WHERE Stock <= 5 AND Activo = 1"
    }
    
    params = {
        "ventas_mes": (first_day_of_month,),
        "gastos_mes": (first_day_of_month,),
        "ventas_hoy": (today,),
        "stock_bajo": ()
    }
    
    results = {}
    
    for key, query in queries.items():
        data, error = _execute_query(query, params[key], fetch_one=True)
        if error or not data:
            results[key] = 0.0
        else:
            results[key] = data[0] if data[0] is not None else 0.0

    balance = results["ventas_mes"] - results["gastos_mes"]
    
    return {
        "ventas_mes": f"${results['ventas_mes']:.2f}",
        "gastos_mes": f"${results['gastos_mes']:.2f}",
        "balance_mes": f"${balance:.2f}",
        "stock_bajo": str(int(results['stock_bajo']))
    }

def get_chart_data():
    query = """
        SELECT TOP 7 
            CONVERT(date, FechaVenta) AS Dia,
            SUM(Total) AS TotalVentas
        FROM Ventas
        GROUP BY CONVERT(date, FechaVenta)
        ORDER BY Dia DESC
    """
    data, error = _execute_query(query, fetch_all=True)
    
    if error or not data:
        return [], []
        
    data.reverse()
    
    labels = [row.Dia.strftime('%d/%m') for row in data]
    values = [float(row.TotalVentas) for row in data]
    
    return labels, values

def get_reports_data(start_date, end_date):
    query = """
        SELECT 
            v.idVenta, 
            v.FechaVenta, 
            u.NombreCompleto AS Usuario, 
            v.Total
        FROM Ventas v
        JOIN Usuarios u ON v.idUsuario = u.idUsuario
        WHERE CONVERT(date, v.FechaVenta) BETWEEN ? AND ?
        ORDER BY v.FechaVenta DESC
    """
    params = (start_date, end_date)
    data, error = _execute_query(query, params, fetch_all=True)
    return data, error