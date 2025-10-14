import bcrypt
from app.database import get_connection

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)

def check_password(hashed_password, user_password):
    user_password_bytes = user_password.encode('utf-8')
    return bcrypt.checkpw(user_password_bytes, hashed_password)

def create_user(username, password, full_name, role_id):
    hashed = hash_password(password)
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Usuarios (NombreUsuario, Contrasena, NombreCompleto, idRol) VALUES (?, ?, ?, ?)"
        cursor.execute(query, username, hashed, full_name, role_id)
        conn.commit()
        print(f"✅ Usuario '{username}' creado exitosamente.")
        return True
    except Exception as e:
        if 'UNIQUE KEY' in str(e):
            print(f"⚠️ El usuario '{username}' ya existe.")
        else:
            print(f"❌ Error al crear el usuario: {e}")
        return False
    finally:
        if conn: conn.close()

def verify_user(username, password):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        query = """
            SELECT u.Contrasena, r.NombreRol
            FROM Usuarios u JOIN Roles r ON u.idRol = r.idRol
            WHERE u.NombreUsuario = ? AND u.Activo = 1
        """
        cursor.execute(query, username)
        user_data = cursor.fetchone()
        
        if user_data and check_password(user_data.Contrasena, password):
            return user_data.NombreRol
        return None
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return None
    finally:
        if conn: conn.close()