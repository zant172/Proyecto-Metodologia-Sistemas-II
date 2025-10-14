import pyodbc

SERVER = 'ZANLAPT\SQLEXPRESS'
DATABASE = 'InfinityTech'

def get_connection():
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

if __name__ == '__main__':
    print("Intentando conectar a la base de datos con Driver 18...")
    conn = get_connection()
    if conn:
        print("✅ ¡Prueba de conexión exitosa! La conexión se estableció y se cerrará.")
        conn.close()
    else:
        print("❌ La prueba de conexión falló. Revisa el nombre del servidor.")