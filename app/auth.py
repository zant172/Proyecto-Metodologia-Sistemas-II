import bcrypt
from .database import get_connection

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)

def check_password(hashed_password, user_password):
    user_password_bytes = user_password.encode('utf-8')
    return bcrypt.checkpw(user_password_bytes, hashed_password)

def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
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
        if commit:
            conn.commit()
            result = True
        elif fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        return result, None
    
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

def ensure_superadmin_exists():
    print("--- Verificando existencia del Super Admin ---")
    
    query_check = "SELECT COUNT(*) FROM Usuarios WHERE idRol = 1"
    count_data, error = _execute_query(query_check, fetch_one=True)
    
    if error:
        print(f"❌ Error al verificar Super Admin: {error}")
        return
    
    if count_data and count_data[0] > 0:
        print("✅ Super Admin ya existe. Omitiendo creación.")
        return

    print("ℹ️  No se encontró Super Admin. Creando cuenta 'sprsjg26'...")
    
    username = 'sprsjg26'
    password = 'superadminpass'
    full_name = 'Desarrollador del Sistema'
    role_id = 1
    
    hashed = hash_password(password)
    query_create = """
        INSERT INTO Usuarios (NombreUsuario, Contrasena, NombreCompleto, idRol, Activo) 
        VALUES (?, ?, ?, ?, 1)
    """
    params = (username, hashed, full_name, role_id)
    success, error = _execute_query(query_create, params, commit=True)
    
    if success:
        print(f"✅ ¡Cuenta Super Admin '{username}' creada exitosamente!")
    else:
        print(f"❌ Error crítico al crear Super Admin: {error}")

def verify_user(username, password):
    query = """
        SELECT u.Contrasena, r.NombreRol, u.idUsuario
        FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol
        WHERE u.NombreUsuario = ? AND u.Activo = 1
    """
    user_data, error = _execute_query(query, (username,), fetch_one=True)
    
    if user_data and check_password(user_data.Contrasena, password):
        return user_data.NombreRol, user_data.idUsuario
    
    if error:
        print(f"❌ Error durante la verificación: {error}")
        
    return None, None

def create_user(username, password, full_name, role_id):
    hashed = hash_password(password)
    query = """
        INSERT INTO Usuarios (NombreUsuario, Contrasena, NombreCompleto, idRol, Activo) 
        VALUES (?, ?, ?, ?, 1)
    """
    params = (username, hashed, full_name, role_id)
    success, error = _execute_query(query, params, commit=True)
    
    if success:
        print(f"✅ Usuario '{username}' creado exitosamente.")
        return True, "Usuario creado exitosamente."
    else:
        if 'UNIQUE KEY' in str(error):
            return False, f"El usuario '{username}' ya existe."
        return False, f"Error al crear usuario: {error}"

def get_all_users():
    query = """
        SELECT u.idUsuario, u.NombreUsuario, u.NombreCompleto, r.NombreRol
        FROM Usuarios u
        JOIN Roles r ON u.idRol = r.idRol
        WHERE u.Activo = 1 AND u.idRol != 1 
        ORDER BY u.NombreCompleto
    """
    users, error = _execute_query(query, fetch_all=True)
    return users, error

def get_user_by_id(user_id):
    query = "SELECT NombreUsuario, NombreCompleto, idRol FROM Usuarios WHERE idUsuario = ?"
    user, error = _execute_query(query, (user_id,), fetch_one=True)
    return user, error

def get_all_roles():
    query = "SELECT idRol, NombreRol FROM Roles WHERE idRol != 1 ORDER BY NombreRol"
    roles, error = _execute_query(query, fetch_all=True)
    return roles, error

def update_user(user_id, username, full_name, role_id, new_password=None):
    try:
        conn = get_connection()
        if not conn: return False, "Error de conexión."
        
        cursor = conn.cursor()
        
        if new_password:
            hashed = hash_password(new_password)
            query = """
                UPDATE Usuarios 
                SET NombreUsuario = ?, NombreCompleto = ?, idRol = ?, Contrasena = ?
                WHERE idUsuario = ?
            """
            params = (username, full_name, role_id, hashed, user_id)
        else:
            query = """
                UPDATE Usuarios 
                SET NombreUsuario = ?, NombreCompleto = ?, idRol = ?
                WHERE idUsuario = ?
            """
            params = (username, full_name, role_id, user_id)
            
        cursor.execute(query, params)
        conn.commit()
        return True, "Usuario actualizado exitosamente."
    
    except Exception as e:
        if 'UNIQUE KEY' in str(e):
            return False, f"El nombre de usuario '{username}' ya existe."
        return False, f"Error al actualizar usuario: {e}"
    finally:
        if conn: conn.close()

def delete_user(user_id):
    query = "UPDATE Usuarios SET Activo = 0 WHERE idUsuario = ?"
    success, error = _execute_query(query, (user_id,), commit=True)
    
    if success:
        return True, "Usuario eliminado exitosamente."
    else:
        return False, f"Error al eliminar usuario: {error}"