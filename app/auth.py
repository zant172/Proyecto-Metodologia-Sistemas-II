import bcrypt
from .database import get_connection # <--- CORRECCIÓN DE IMPORT RELATIVO

# --- Funciones de Hashing (sin cambios) ---
def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)

def check_password(hashed_password, user_password):
    user_password_bytes = user_password.encode('utf-8')
    return bcrypt.checkpw(user_password_bytes, hashed_password)

# --- Función auxiliar (para manejo limpio de BD) ---
def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    """Función auxiliar para manejar la lógica de la base de datos."""
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
            result = True # Para operaciones de commit, devolvemos éxito
        elif fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        return result, None # (Datos, Error)
    
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

# --- Funciones de Autenticación y CRUD de Usuarios ---

def verify_user(username, password):
    """Verifica el login de un usuario y devuelve su rol."""
    query = """
        SELECT u.Contrasena, r.NombreRol
        FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol
        WHERE u.NombreUsuario = ? AND u.Activo = 1
    """
    user_data, error = _execute_query(query, (username,), fetch_one=True)
    
    if user_data and check_password(user_data.Contrasena, password):
        return user_data.NombreRol
    
    if error:
        print(f"❌ Error durante la verificación: {error}")
        
    return None

def create_user(username, password, full_name, role_id):
    """Crea un nuevo usuario (usado por setup y el admin)."""
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

# --- NUEVAS FUNCIONES PARA GESTIÓN DE USUARIOS ---

def get_all_users():
    """Obtiene todos los usuarios activos y su rol, excepto el superadmin (idRol=1)."""
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
    """Obtiene los datos de un usuario por ID."""
    query = "SELECT NombreUsuario, NombreCompleto, idRol FROM Usuarios WHERE idUsuario = ?"
    user, error = _execute_query(query, (user_id,), fetch_one=True)
    return user, error

def get_all_roles():
    """Obtiene todos los roles (para el QComboBox), excepto superadmin."""
    # Asumimos que "superadmin" es idRol=1
    query = "SELECT idRol, NombreRol FROM Roles WHERE idRol != 1 ORDER BY NombreRol"
    roles, error = _execute_query(query, fetch_all=True)
    return roles, error

def update_user(user_id, username, full_name, role_id, new_password=None):
    """Actualiza un usuario. Opcionalmente cambia la contraseña si se provee una."""
    try:
        conn = get_connection()
        if not conn: return False, "Error de conexión."
        
        cursor = conn.cursor()
        
        if new_password:
            # Si se provee una nueva contraseña, la hasheamos y actualizamos
            hashed = hash_password(new_password)
            query = """
                UPDATE Usuarios 
                SET NombreUsuario = ?, NombreCompleto = ?, idRol = ?, Contrasena = ?
                WHERE idUsuario = ?
            """
            params = (username, full_name, role_id, hashed, user_id)
        else:
            # Si no, actualizamos todo excepto la contraseña
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
    """Desactiva un usuario (borrado lógico)."""
    query = "UPDATE Usuarios SET Activo = 0 WHERE idUsuario = ?"
    success, error = _execute_query(query, (user_id,), commit=True)
    
    if success:
        return True, "Usuario eliminado exitosamente."
    else:
        return False, f"Error al eliminar usuario: {error}"