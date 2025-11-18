"""
Módulo para generación de reportes
"""
from .database import get_connection
from datetime import datetime, timedelta


def get_ventas_por_fecha(fecha_inicio, fecha_fin):
    """Obtiene ventas entre dos fechas"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.idVenta, v.FechaVenta, v.Total, mp.Nombre as metodo_pago,
                   u.NombreCompleto as usuario
            FROM Ventas v
            LEFT JOIN MetodosPago mp ON v.idMetodoPago = mp.idMetodoPago
            LEFT JOIN Usuarios u ON v.idUsuario = u.idUsuario
            WHERE CAST(v.FechaVenta AS DATE) BETWEEN ? AND ?
            ORDER BY v.FechaVenta DESC
        """, (fecha_inicio, fecha_fin))
        
        ventas = []
        for row in cursor.fetchall():
            ventas.append({
                'id': row[0],
                'fecha': row[1],
                'total': float(row[2]),
                'metodo_pago': row[3],
                'usuario': row[4]
            })
        return ventas
    except Exception as e:
        print(f"Error al obtener ventas por fecha: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_gastos_por_fecha(fecha_inicio, fecha_fin):
    """Obtiene gastos entre dos fechas"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.idGasto, g.FechaGasto, g.Descripcion, g.Monto, g.Categoria
            FROM Gastos g
            WHERE CAST(g.FechaGasto AS DATE) BETWEEN ? AND ?
            ORDER BY g.FechaGasto DESC
        """, (fecha_inicio, fecha_fin))
        
        gastos = []
        for row in cursor.fetchall():
            gastos.append({
                'id': row[0],
                'fecha': row[1],
                'descripcion': row[2],
                'monto': float(row[3]),
                'categoria': row[4] or ''
            })
        return gastos
    except Exception as e:
        print(f"Error al obtener gastos por fecha: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_resumen_financiero(fecha_inicio, fecha_fin):
    """Obtiene resumen financiero entre dos fechas"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Total ventas
        cursor.execute("""
            SELECT ISNULL(SUM(Total), 0)
            FROM Ventas
            WHERE CAST(FechaVenta AS DATE) BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        total_ventas = float(cursor.fetchone()[0])
        
        # Total gastos
        cursor.execute("""
            SELECT ISNULL(SUM(Monto), 0)
            FROM Gastos
            WHERE CAST(FechaGasto AS DATE) BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        total_gastos = float(cursor.fetchone()[0])
        
        # Cantidad de ventas
        cursor.execute("""
            SELECT COUNT(*)
            FROM Ventas
            WHERE CAST(FechaVenta AS DATE) BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        cantidad_ventas = cursor.fetchone()[0]
        
        # Productos más vendidos
        cursor.execute("""
            SELECT TOP 5 p.NombreProducto, SUM(dv.Cantidad) as total_vendido
            FROM DetalleVentas dv
            JOIN Productos p ON dv.idProducto = p.idProducto
            JOIN Ventas v ON dv.idVenta = v.idVenta
            WHERE CAST(v.FechaVenta AS DATE) BETWEEN ? AND ?
            GROUP BY p.NombreProducto
            ORDER BY total_vendido DESC
        """, (fecha_inicio, fecha_fin))
        top_productos = []
        for row in cursor.fetchall():
            top_productos.append({
                'nombre': row[0],
                'cantidad': row[1]
            })
        
        return {
            'total_ventas': total_ventas,
            'total_gastos': total_gastos,
            'balance': total_ventas - total_gastos,
            'cantidad_ventas': cantidad_ventas,
            'top_productos': top_productos
        }
    except Exception as e:
        print(f"Error al obtener resumen financiero: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def get_ventas_por_metodo_pago(fecha_inicio, fecha_fin):
    """Obtiene ventas agrupadas por método de pago"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mp.Nombre, COUNT(v.idVenta) as cantidad, ISNULL(SUM(v.Total), 0) as total
            FROM Ventas v
            LEFT JOIN MetodosPago mp ON v.idMetodoPago = mp.idMetodoPago
            WHERE CAST(v.FechaVenta AS DATE) BETWEEN ? AND ?
            GROUP BY mp.Nombre
            ORDER BY total DESC
        """, (fecha_inicio, fecha_fin))
        
        resultado = []
        for row in cursor.fetchall():
            resultado.append({
                'metodo': row[0] or 'Sin método',
                'cantidad': row[1],
                'total': float(row[2])
            })
        return resultado
    except Exception as e:
        print(f"Error al obtener ventas por método de pago: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
