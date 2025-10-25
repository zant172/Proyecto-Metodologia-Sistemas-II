import bcrypt
from .database import get_connection

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    if not conn: return None, "Error de conexión."
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = None
        if commit: conn.commit(); result = True
        elif fetch_one: result = cursor.fetchone()
        elif fetch_all: result = cursor.fetchall()
        return result, None
    except Exception as e: return None, str(e)
    finally:
        if conn: conn.close()

def verify_user(username, password):
    query = "SELECT u.Contrasena, r.NombreRol, u.idUsuario FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol WHERE u.NombreUsuario = ? AND u.Activo = 1"
    user_data, error = _execute_query(query, (username,), fetch_one=True)
    if user_data and check_password(user_data.Contrasena, password):
        return user_data.NombreRol, user_data.idUsuario
    if error: print(f"❌ Error verificación: {error}")
    return None, None

def create_user(username, password, full_name, role_id):
    hashed = hash_password(password)
    query = "INSERT INTO Usuarios (NombreUsuario, Contrasena, NombreCompleto, idRol, Activo) VALUES (?, ?, ?, ?, 1)"
    success, error = _execute_query(query, (username, hashed, full_name, role_id), commit=True)
    if success: print(f"✅ Usuario '{username}' creado."); return True, "Usuario creado."
    msg = f"El usuario '{username}' ya existe." if error and 'UNIQUE KEY' in error else f"Error al crear: {error}"
    return False, msg

def get_all_users():
    query = "SELECT u.idUsuario, u.NombreUsuario, u.NombreCompleto, r.NombreRol FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol WHERE u.Activo = 1 AND u.idRol != 1 ORDER BY u.NombreCompleto"
    return _execute_query(query, fetch_all=True)

def get_user_by_id(user_id):
    query = "SELECT NombreUsuario, NombreCompleto, idRol FROM Usuarios WHERE idUsuario = ?"
    return _execute_query(query, (user_id,), fetch_one=True)

def get_all_roles():
    query = "SELECT idRol, NombreRol FROM Roles WHERE idRol != 1 ORDER BY NombreRol"
    return _execute_query(query, fetch_all=True)

def update_user(user_id, username, full_name, role_id, new_password=None):
    conn = get_connection()
    if not conn: return False, "Error de conexión."
    try:
        cursor = conn.cursor()
        if new_password:
            hashed = hash_password(new_password)
            query = "UPDATE Usuarios SET NombreUsuario = ?, NombreCompleto = ?, idRol = ?, Contrasena = ? WHERE idUsuario = ?"
            params = (username, full_name, role_id, hashed, user_id)
        else:
            query = "UPDATE Usuarios SET NombreUsuario = ?, NombreCompleto = ?, idRol = ? WHERE idUsuario = ?"
            params = (username, full_name, role_id, user_id)
        cursor.execute(query, params)
        conn.commit()
        return True, "Usuario actualizado."
    except Exception as e:
        msg = f"El usuario '{username}' ya existe." if 'UNIQUE KEY' in str(e) else f"Error al actualizar: {e}"
        return False, msg
    finally:
        if conn: conn.close()

def delete_user(user_id):
    query = "UPDATE Usuarios SET Activo = 0 WHERE idUsuario = ?"
    success, error = _execute_query(query, (user_id,), commit=True)
    return (True, "Usuario eliminado.") if success else (False, f"Error al eliminar: {error}")