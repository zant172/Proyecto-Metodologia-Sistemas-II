import pyodbc
import configparser
import os
import time

config = configparser.ConfigParser()
ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_config = os.path.join(ruta_base, 'config.ini')

# Nuevo nombre de base de datos por defecto
DEFAULT_DB_NAME = "sistemgestionvntsjg"

try:
    config.read(ruta_config)
    SERVER = config.get('Database', 'SERVER', fallback='localhost\\SQLEXPRESS')
    # Lee el nombre de la BD desde config.ini, usa DEFAULT_DB_NAME si falta
    DATABASE = config.get('Database', 'DATABASE', fallback=DEFAULT_DB_NAME)
    USERNAME = config.get('Database', 'USERNAME', fallback=None)
    PASSWORD = config.get('Database', 'PASSWORD', fallback=None)
    print(f"✅ Configuración cargada: Server={SERVER}, DB={DATABASE}")
except Exception as e:
    print(f"❌ Error al leer config.ini: {e}. Usando defaults.")
    SERVER = 'localhost\\SQLEXPRESS'
    DATABASE = DEFAULT_DB_NAME # Usa el nuevo default
    USERNAME = None
    PASSWORD = None

def get_db_connection_string(db_name):
    # Genera la cadena de conexión para una base de datos específica
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={db_name};"
        f"TrustServerCertificate=yes;"
    )
    if USERNAME and PASSWORD and USERNAME.strip():
        connection_string += f"UID={USERNAME};PWD={PASSWORD};"
    else:
        connection_string += "Trusted_Connection=yes;"
    return connection_string

def get_connection(db_name=DATABASE):
    # Se conecta a la base de datos especificada (por defecto, la configurada)
    try:
        conn_str = get_db_connection_string(db_name)
        return pyodbc.connect(conn_str, autocommit=False)
    except Exception as e:
        print(f"❌ Error al conectar a DB '{db_name}': {e}")
        return None

def check_database_exists():
    # Verifica si la base de datos principal (DATABASE) existe
    print(f"--- Verificando existencia de DB '{DATABASE}' ---")
    conn_master = None
    try:
        # Conexión a 'master'
        master_conn_str = get_db_connection_string('master')
        conn_master = pyodbc.connect(master_conn_str, autocommit=True)
        cursor = conn_master.cursor()
        cursor.execute("SELECT COUNT(*) FROM sys.databases WHERE name = ?", (DATABASE,))
        exists = cursor.fetchone()[0] > 0
        if exists: print(f"✅ DB '{DATABASE}' ya existe.")
        else: print(f"ℹ️  DB '{DATABASE}' no existe.")
        return exists
    except Exception as e:
        print(f"❌ Error verificando existencia de DB '{DATABASE}': {e}")
        return False
    finally:
        if conn_master: conn_master.close()

def create_database():
    # Intenta crear la base de datos principal
    print(f"--- Intentando crear DB '{DATABASE}' ---")
    conn_master = None
    try:
        master_conn_str = get_db_connection_string('master')
        conn_master = pyodbc.connect(master_conn_str, autocommit=True)
        cursor = conn_master.cursor()
        # Usa el nuevo nombre DATABASE al crear
        cursor.execute(f"CREATE DATABASE [{DATABASE}]")
        print(f"✅ DB '{DATABASE}' creada.")
        time.sleep(2) # Pausa breve
        return True
    except Exception as e:
        print(f"❌ Error crítico al crear DB '{DATABASE}': {e}")
        print("   Verifica permisos 'dbcreator'.")
        return False
    finally:
        if conn_master: conn_master.close()

def check_schema_exists(conn):
    # Verifica si la tabla 'Roles' existe dentro de la BD conectada
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'Roles'")
        exists = cursor.fetchone()[0] > 0
        return exists
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def initialize_database_schema():
    # Flujo completo: Verifica/Crea BD -> Verifica/Crea Tablas
    print("--- Iniciando inicialización DB ---")
    if not check_database_exists():
        if not create_database(): return False # Detiene si no se puede crear BD

    conn = get_connection(DATABASE) # Conecta a la BD (recién creada o existente)
    if not conn:
        print(f"❌ No se pudo conectar a '{DATABASE}'.")
        return False

    if check_schema_exists(conn):
        print("✅ Esquema (tablas) ya existe.")
        conn.close(); return True # Todo listo

    print("ℹ️  Esquema (tablas) no existe. Creando...")
    try:
        cursor = conn.cursor()
        # El script SQL para crear tablas sigue igual, se ejecuta DENTRO de la BD correcta
        sql_script = """
        CREATE TABLE Roles ( idRol INT IDENTITY(1,1) PRIMARY KEY, NombreRol NVARCHAR(50) NOT NULL UNIQUE );
        CREATE TABLE Usuarios ( idUsuario INT IDENTITY(1,1) PRIMARY KEY, NombreUsuario NVARCHAR(100) NOT NULL UNIQUE, NombreCompleto NVARCHAR(200) NOT NULL, Contrasena VARBINARY(60) NOT NULL, idRol INT NOT NULL, Activo BIT NOT NULL DEFAULT 1, CONSTRAINT FK_Usuarios_Roles FOREIGN KEY (idRol) REFERENCES Roles(idRol) );
        CREATE TABLE Categorias ( idCategoria INT IDENTITY(1,1) PRIMARY KEY, NombreCategoria NVARCHAR(100) NOT NULL UNIQUE );
        CREATE TABLE Productos ( idProducto INT IDENTITY(1,1) PRIMARY KEY, Codigo NVARCHAR(50) NOT NULL UNIQUE, NombreProducto NVARCHAR(200) NOT NULL UNIQUE, idCategoria INT NOT NULL, Precio DECIMAL(10, 2) NOT NULL, Stock INT NOT NULL DEFAULT 0, Activo BIT NOT NULL DEFAULT 1, CONSTRAINT FK_Productos_Categorias FOREIGN KEY (idCategoria) REFERENCES Categorias(idCategoria) );
        CREATE TABLE Ventas ( idVenta INT IDENTITY(1,1) PRIMARY KEY, idUsuario INT NOT NULL, Total DECIMAL(10, 2) NOT NULL, FechaVenta DATETIME NOT NULL DEFAULT GETDATE(), CONSTRAINT FK_Ventas_Usuarios FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario) );
        CREATE TABLE DetalleVentas ( idDetalleVenta INT IDENTITY(1,1) PRIMARY KEY, idVenta INT NOT NULL, idProducto INT NOT NULL, Cantidad INT NOT NULL, PrecioUnitario DECIMAL(10, 2) NOT NULL, CONSTRAINT FK_DetalleVentas_Ventas FOREIGN KEY (idVenta) REFERENCES Ventas(idVenta), CONSTRAINT FK_DetalleVentas_Productos FOREIGN KEY (idProducto) REFERENCES Productos(idProducto) );
        CREATE TABLE Gastos ( idGasto INT IDENTITY(1,1) PRIMARY KEY, Descripcion NVARCHAR(255) NOT NULL, Monto DECIMAL(10, 2) NOT NULL, Categoria NVARCHAR(100) NULL, FechaGasto DATE NOT NULL DEFAULT GETDATE() );
        CREATE TABLE Configuracion ( idConfig INT IDENTITY(1,1) PRIMARY KEY, NombreNegocio NVARCHAR(200) NULL, TipoNegocio NVARCHAR(100) NULL, SetupCompleto BIT NOT NULL DEFAULT 0 );
        INSERT INTO Roles (NombreRol) VALUES ('Dev'), ('Admin'), ('Usuario');
        INSERT INTO Configuracion (SetupCompleto) VALUES (0);
        """
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
        for command in commands:
            if command: cursor.execute(command)
        conn.commit()
        print("✅ Esquema (tablas) creado.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error crítico al crear tablas: {e}")
        return False
    finally:
        if conn: conn.close()

# Bloque de prueba
if __name__ == '__main__':
    if initialize_database_schema():
        print("Intentando conectar a DB final...")
        conn = get_connection()
        if conn: print("✅ Conexión final OK!"); conn.close()
        else: print("❌ Conexión final falló.")
    else:
        print("❌ Inicialización completa falló.")