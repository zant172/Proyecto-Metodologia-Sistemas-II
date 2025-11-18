"""
Módulo para gestión de gastos
"""
from .database import get_connection
from datetime import datetime


def get_all_gastos():
    """Obtiene todos los gastos registrados"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.idGasto, g.Descripcion, g.Monto, g.FechaGasto, g.Categoria, g.Nota
            FROM Gastos g
            ORDER BY g.FechaGasto DESC
        """)
        gastos = []
        for row in cursor.fetchall():
            gastos.append({
                'id': row[0],
                'descripcion': row[1],
                'monto': float(row[2]),
                'fecha': row[3],
                'categoria': row[4] or '',
                'nota': row[5] or ''
            })
        return gastos
    except Exception as e:
        print(f"Error al obtener gastos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def create_gasto(descripcion, monto, categoria='', nota=''):
    """Crea un nuevo gasto"""
    if not descripcion or not descripcion.strip():
        return False, "La descripción es obligatoria"
    
    if monto <= 0:
        return False, "El monto debe ser mayor a 0"
    
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Gastos (Descripcion, Monto, FechaGasto, Categoria, Nota)
            VALUES (?, ?, CAST(GETDATE() AS DATE), ?, ?)
        """, (descripcion, monto, categoria if categoria else None, nota if nota else None))
        conn.commit()
        return True, "Gasto registrado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al crear gasto: {e}")
        return False, f"Error al registrar gasto: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def update_gasto(gasto_id, descripcion, monto, categoria='', nota=''):
    """Actualiza un gasto existente"""
    if not descripcion or not descripcion.strip():
        return False, "La descripción es obligatoria"
    
    if monto <= 0:
        return False, "El monto debe ser mayor a 0"
    
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Gastos
            SET Descripcion = ?, Monto = ?, Categoria = ?, Nota = ?
            WHERE idGasto = ?
        """, (descripcion, monto, categoria if categoria else None, nota if nota else None, gasto_id))
        conn.commit()
        return True, "Gasto actualizado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar gasto: {e}")
        return False, f"Error al actualizar gasto: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def delete_gasto(gasto_id):
    """Elimina un gasto"""
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Gastos WHERE idGasto = ?", (gasto_id,))
        conn.commit()
        return True, "Gasto eliminado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar gasto: {e}")
        return False, f"Error al eliminar gasto: {str(e)}"
    finally:
        cursor.close()
        conn.close()
