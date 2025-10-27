import pyodbc
import configparser
import os

config = configparser.ConfigParser()

ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_config = os.path.join(ruta_base, 'config.ini')

try:
    config.read(ruta_config)
    
    SERVER = config.get('Database', 'SERVER', fallback='localhost\SQLEXPRESS')
    DATABASE = config.get('Database', 'DATABASE', fallback='InfinityTech')
    
    USERNAME = config.get('Database', 'USERNAME', fallback=None)
    PASSWORD = config.get('Database', 'PASSWORD', fallback=None)
    
    print(f"✅ Configuración cargada: Conectando a {SERVER} -> {DATABASE}")

except Exception as e:
    print(f"❌ Error al leer config.ini: {e}. Usando valores por defecto.")
    SERVER = 'localhost\SQLEXPRESS'
    DATABASE = 'InfinityTech'
    USERNAME = None
    PASSWORD = None


def get_connection():
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"TrustServerCertificate=yes;"
        )
        
        if USERNAME and PASSWORD and USERNAME.strip():
            connection_string += f"UID={USERNAME};PWD={PASSWORD};"
            print("...usando autenticación SQL (Usuario/Contraseña).")
        else:
            connection_string += "Trusted_Connection=yes;"
            print("...usando autenticación de Windows (Trusted Connection).")
        
        return pyodbc.connect(connection_string)
    
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

if __name__ == '__main__':
    print("Intentando conectar a la base de datos...")
    conn = get_connection()
    if conn:
        print("✅ ¡Prueba de conexión exitosa! La conexión se estableció y se cerrará.")
        conn.close()
    else:
        print("❌ La prueba de conexión falló. Revisa el config.ini.")