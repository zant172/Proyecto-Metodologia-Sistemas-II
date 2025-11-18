"""
Módulo para gestión de métodos de pago
"""
from .database import get_connection


def get_all_metodos_pago():
    """Obtiene todos los métodos de pago"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT idMetodoPago, Nombre, TipoMetodo, Activo FROM MetodosPago ORDER BY Nombre")
        metodos = []
        for row in cursor.fetchall():
            metodos.append({
                'id': row[0],
                'nombre': row[1],
                'tipo': row[2],
                'activo': bool(row[3])
            })
        return metodos
    except Exception as e:
        print(f"Error al obtener métodos de pago: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def create_metodo_pago(nombre, tipo='Efectivo'):
    """Crea un nuevo método de pago"""
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio"
    
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO MetodosPago (Nombre, TipoMetodo, Activo)
            VALUES (?, ?, 1)
        """, (nombre, tipo))
        conn.commit()
        return True, "Método de pago creado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al crear método de pago: {e}")
        return False, f"Error al crear método de pago: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def update_metodo_pago(metodo_id, nombre, tipo, activo):
    """Actualiza un método de pago existente"""
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio"
    
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE MetodosPago
            SET Nombre = ?, TipoMetodo = ?, Activo = ?
            WHERE idMetodoPago = ?
        """, (nombre, tipo, activo, metodo_id))
        conn.commit()
        return True, "Método de pago actualizado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar método de pago: {e}")
        return False, f"Error al actualizar método de pago: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def delete_metodo_pago(metodo_id):
    """Elimina un método de pago"""
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        # Verificar si tiene ventas asociadas
        cursor.execute("SELECT COUNT(*) FROM Ventas WHERE idMetodoPago = ?", (metodo_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return False, f"No se puede eliminar. Hay {count} ventas asociadas a este método de pago"
        
        cursor.execute("DELETE FROM MetodosPago WHERE idMetodoPago = ?", (metodo_id,))
        conn.commit()
        return True, "Método de pago eliminado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar método de pago: {e}")
        return False, f"Error al eliminar método de pago: {str(e)}"
    finally:
        cursor.close()
        conn.close()
