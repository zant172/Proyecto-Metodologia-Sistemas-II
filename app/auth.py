import bcrypt
import sys
from .database import get_connection # Usa la conexión centralizada

# --- Funciones de Contraseña ---
def hash_password(password):
    # Genera un hash seguro para la contraseña usando bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() # Genera una sal aleatoria
    return bcrypt.hashpw(password_bytes, salt) # Devuelve el hash (bytes)

def check_password(hashed_password, user_password):
    # Verifica si la contraseña ingresada coincide con el hash almacenado
    user_password_bytes = user_password.encode('utf-8')
    try:
         # Compara la contraseña en texto plano con el hash de la BD
         if isinstance(hashed_password, bytes): # El hash de la BD es VARBINARY (bytes)
             return bcrypt.checkpw(user_password_bytes, hashed_password)
         else: # Si por alguna razón no fuera bytes, intenta codificar
             return bcrypt.checkpw(user_password_bytes, hashed_password.encode('utf-8'))
    except ValueError: # Captura si el hash tiene formato incorrecto
         print("❌ Error: Hash de contraseña inválido almacenado.")
         return False


# --- Función Auxiliar para Consultas ---
def _execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    # Wrapper reutilizable para ejecutar consultas SQL de forma segura
    conn = get_connection()
    if not conn:
        return None, "Error: No se pudo conectar a la base de datos."
    cursor = None # Inicializa cursor fuera del try
    try:
        cursor = conn.cursor()
        cursor.execute(query, params if params else []) # Ejecuta la consulta
        result = None
        if commit: # Para INSERT, UPDATE, DELETE
            conn.commit() # Confirma cambios
            result = True # Opcional: podrías devolver cursor.rowcount
        elif fetch_one: # Para SELECT que espera una fila
            result = cursor.fetchone()
        elif fetch_all: # Para SELECT que espera múltiples filas
            result = cursor.fetchall()
        return result, None # Éxito: devuelve datos (o True) y None como error
    except Exception as e:
        # Si hay error SQL, intenta deshacer y loguea detalladamente
        try: conn.rollback() # Deshace cambios pendientes
        except Exception as rb_e: print(f"⚠️ Error adicional durante rollback: {rb_e}")
        print(f"❌ Error SQL (_execute_query para '{query[:50]}...') Params={params}: {e}")
        return None, str(e) # Fallo: devuelve None y mensaje de error
    finally:
        # Asegura que la conexión SIEMPRE se cierre
        if cursor: cursor.close() # Cierra cursor si se creó
        if conn: conn.close() # Cierra conexión

# --- Lógica de Super Admin ---
def ensure_superadmin_exists():
    # Verifica al inicio si la cuenta 'sprsjg26' (Rol Dev) existe, y la crea si no
    print("--- Verificando Super Admin ---")
    query_check = "SELECT COUNT(*) FROM Usuarios WHERE idRol = 1"
    count_data, error = _execute_query(query_check, fetch_one=True)
    if error: print(f"❌ Error al verificar Super Admin: {error}"); return # Salir si hay error
    if count_data and count_data[0] > 0: print("✅ Super Admin ya existe."); return # Salir si ya existe

    # Si no existe, procede a crearlo
    print("ℹ️  Creando cuenta Super Admin 'sprsjg26'...")
    username = 'sprsjg26'; password = 'superadminpass'; full_name = 'Desarrollador'; role_id = 1
    hashed = hash_password(password) # Hashea la contraseña
    query_create = "INSERT INTO Usuarios (NombreUsuario, Contrasena, NombreCompleto, idRol, Activo) VALUES (?, ?, ?, ?, 1)"
    success, error = _execute_query(query_create, (username, hashed, full_name, role_id), commit=True)
    if success: print(f"✅ Cuenta Super Admin '{username}' creada.")
    else: print(f"❌ Error crítico al crear Super Admin: {error}") # Loguea error grave

# --- Lógica de Login ---
def verify_user(username, password):
    # Valida usuario y contraseña contra la BD para el login
    query = """
        SELECT u.Contrasena, r.NombreRol, u.idUsuario
        FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol
        WHERE u.NombreUsuario = ? AND u.Activo = 1
    """
    user_data, error = _execute_query(query, (username,), fetch_one=True)
    # Si encuentra usuario Y la contraseña coincide...
    if user_data and check_password(user_data.Contrasena, password):
        print(f"✅ Login exitoso para {username} (Rol: {user_data.NombreRol})")
        return user_data.NombreRol, user_data.idUsuario # Devuelve Rol y ID
    # Si hubo error en la consulta
    if error: print(f"❌ Error durante login query: {error}")
    # Si no encontró usuario o contraseña incorrecta
    print(f"ℹ️  Login fallido para {username}")
    return None, None # Falla login

# --- Gestión de Usuarios (CRUD) ---
def create_user(username, password, full_name, role_id):
    # Crea un NUEVO usuario (usado por asistente y admin)
    # Valida que el rol exista (protección extra)
    role_check, err_role = _execute_query("SELECT COUNT(*) FROM Roles WHERE idRol = ?", (role_id,), fetch_one=True)
    if err_role or not role_check or role_check[0] == 0:
         return False, f"Error: El rol ID {role_id} no es válido."

    hashed = hash_password(password)
    query = "INSERT INTO Usuarios (NombreUsuario, Contrasena, NombreCompleto, idRol, Activo) VALUES (?, ?, ?, ?, 1)"
    success, error = _execute_query(query, (username, hashed, full_name, role_id), commit=True)
    if success: return True, "Usuario creado."
    else:
        # Devuelve mensaje específico si el usuario ya existe
        if error and ('UNIQUE KEY' in error or 'UNIQUE constraint' in error or 'duplicate key' in error):
             return False, f"El nombre de usuario '{username}' ya existe."
        # Mensaje genérico para otros errores
        return False, f"Error al crear usuario: {error or 'Error desconocido'}"

def get_all_users():
    # Obtiene lista de usuarios para mostrar en la tabla (excluye al Dev)
    query = "SELECT u.idUsuario, u.NombreUsuario, u.NombreCompleto, r.NombreRol FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol WHERE u.Activo = 1 AND u.idRol != 1 ORDER BY u.NombreCompleto"
    return _execute_query(query, fetch_all=True)

def get_user_by_id(user_id):
    # Obtiene datos de un usuario para rellenar el formulario de edición
    query = "SELECT NombreUsuario, NombreCompleto, idRol FROM Usuarios WHERE idUsuario = ?"
    return _execute_query(query, (user_id,), fetch_one=True)

def get_all_roles():
    # Obtiene lista de roles para el ComboBox (excluye Dev)
    query = "SELECT idRol, NombreRol FROM Roles WHERE idRol != 1 ORDER BY NombreRol"
    return _execute_query(query, fetch_all=True)

def update_user(user_id, username, full_name, role_id, new_password=None):
    # Actualiza datos de un usuario existente
    try:
        # Construcción dinámica de la consulta UPDATE
        query_parts = ["UPDATE Usuarios SET NombreUsuario = ?, NombreCompleto = ?, idRol = ?"]
        params = [username, full_name, role_id]
        if new_password: # Si se ingresó nueva contraseña
            hashed = hash_password(new_password)
            query_parts.append(", Contrasena = ?")
            params.append(hashed)
        query_parts.append("WHERE idUsuario = ?")
        params.append(user_id)
        query = " ".join(query_parts)

        success, error = _execute_query(query, tuple(params), commit=True)
        if success: return True, "Usuario actualizado."
        else:
            if error and ('UNIQUE KEY' in error or 'UNIQUE constraint' in error or 'duplicate key' in error):
                return False, f"El usuario '{username}' ya está en uso."
            return False, f"Error al actualizar: {error or '?'}"
    except Exception as e: return False, f"Error inesperado: {e}"

def delete_user(user_id):
    # Marca un usuario como inactivo (Soft Delete)
    query = "UPDATE Usuarios SET Activo = 0 WHERE idUsuario = ?"
    success, error = _execute_query(query, (user_id,), commit=True)
    if success: return True, "Usuario inactivado."
    else: return False, f"Error al inactivar: {error or '?'}"

# --- Funciones de Configuración Inicial ---

def is_initial_setup_complete():
    # Verifica si el flag SetupCompleto es 1 en la tabla Configuracion
    # Es crucial para decidir si mostrar el asistente o MainWindow
    query = "SELECT TOP 1 SetupCompleto FROM Configuracion ORDER BY idConfig" # Asegura tomar la primera fila
    result, error = _execute_query(query, fetch_one=True)
    if error: print(f"❌ Error verificando setup: {error}"); return False # Asume no completo si hay error
    if result and result[0] == 1: print("✅ Setup completo."); return True
    else: print("ℹ️  Setup pendiente."); return False

def mark_setup_complete(nombre_negocio, tipo_negocio):
    # Guarda Nombre/Tipo de negocio y marca SetupCompleto = 1
    # Se usa al finalizar el asistente
    query = "UPDATE Configuracion SET NombreNegocio = ?, TipoNegocio = ?, SetupCompleto = 1 WHERE idConfig = (SELECT MIN(idConfig) FROM Configuracion)"
    success, error = _execute_query(query, (nombre_negocio, tipo_negocio), commit=True)
    if not success: print(f"❌ Error marcando setup completo: {error}")
    return success

def create_default_categories(business_type):
    # Inserta categorías predefinidas según el Tipo de Negocio elegido
    print(f"--- Creando categorías default para: {business_type} ---")
    cats = [] # Lista para almacenar las categorías
    # Define las listas según el tipo de negocio
    if business_type == "Kiosko / Almacén": cats = ["Bebidas", "Alimentos Secos", "Limpieza", "Golosinas", "Lácteos", "Panificados", "Cigarrillos", "Recargas", "Otros"]
    elif business_type == "Ferretería": cats = ["Herramientas Manuales", "Herramientas Eléctricas", "Electricidad", "Pinturas", "Fontanería", "Tornillería", "Jardinería", "Seguridad", "Otros"]
    elif business_type == "Tienda de Ropa": cats = ["Remeras", "Pantalones", "Jeans", "Calzado", "Accesorios", "Abrigos", "Ropa Interior", "Vestidos", "Otros"]
    elif business_type == "Tienda de Electrónicos": cats = ["Celulares", "Accesorios Celulares", "Computadoras", "Componentes PC", "Audio y Video", "Cables y Conectores", "Gaming", "Otros"]
    elif business_type == "Otro / Mixto": cats = ["General", "Varios", "Servicios", "Otros"]
    # Si no se definió lista para el tipo, no hace nada
    if not cats: print("ℹ️  Sin categorías default."); return True

    query = "INSERT INTO Categorias (NombreCategoria) VALUES (?)"
    ok, skip = 0, 0 # Contadores
    conn = get_connection() # Necesita conexión para manejar errores de duplicados
    if not conn: return False
    try:
        cursor = conn.cursor()
        for cat in cats: # Itera e intenta insertar cada categoría
            try: cursor.execute(query, (cat,)); ok += 1; print(f"✅ Cat: '{cat}'")
            except Exception as e: # Si falla (probablemente por duplicado)
                 # Verifica si el error es por clave única duplicada
                 if 'UNIQUE KEY' in str(e) or 'UNIQUE constraint' in str(e) or 'duplicate key' in str(e): skip += 1; print(f"ℹ️  Cat: '{cat}' ya existe.")
                 else: raise e # Si es otro error, lo propaga
        conn.commit(); print(f"-> Cats creadas: {ok}, Omitidas: {skip}"); return True
    except Exception as e: conn.rollback(); print(f"❌ Error creando cats: {e}"); return False
    finally:
        if conn: conn.close() # Cierra conexión