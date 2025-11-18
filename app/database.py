import pyodbc
import os
import time

# --- Parámetros de Conexión Globales (inicializados con defaults) ---
_SERVER = 'localhost\\SQLEXPRESS'
_DATABASE = 'sistemgestionvntsjg'
_USERNAME = None
_PASSWORD = None
_TRUSTED = True # Default a Windows Auth

def set_connection_parameters(server, database, username=None, password=None, trusted=True):
    # Función llamada por main.py para configurar la conexión de esta sesión
    global _SERVER, _DATABASE, _USERNAME, _PASSWORD, _TRUSTED
    _SERVER = server
    _DATABASE = database
    _USERNAME = username
    _PASSWORD = password
    _TRUSTED = trusted
    print(f"ℹ️  Parámetros de conexión en memoria: Srv={_SERVER}, DB={_DATABASE}, Trusted={_TRUSTED}, Usr={_USERNAME is not None}")

def get_db_connection_string(db_name):
    # Construye la cadena usando los parámetros globales _SERVER, _USERNAME, etc.
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={_SERVER};"
        f"DATABASE={db_name};"
        f"TrustServerCertificate=yes;"
    )
    if not _TRUSTED and _USERNAME and _PASSWORD is not None:
        connection_string += f"UID={_USERNAME};PWD={_PASSWORD};"
    else: # Si es Trusted o si faltan user/pass en modo SQL Auth
        connection_string += "Trusted_Connection=yes;"
    return connection_string

def get_connection(db_name=None):
    # Obtiene una conexión usando los parámetros globales actuales
    # Si db_name es None, usa _DATABASE global (que debe estar inicializado)
    if db_name is None:
        db_name = _DATABASE
    try:
        conn_str = get_db_connection_string(db_name)
        return pyodbc.connect(conn_str, autocommit=False) # autocommit=False: transacciones manuales
    except Exception as e:
        print(f"❌ Error al conectar a DB '{db_name}': {e}")
        return None

# --- Funciones de Inicialización (dependen de get_connection) ---

def check_database_exists():
    # Verifica si la BD principal (_DATABASE) existe conectándose a 'master'
    print(f"--- Verificando existencia de DB '{_DATABASE}' ---")
    conn_master = None
    try:
        conn_master = get_connection('master') # Usa los parámetros actuales para conectar a master
        if not conn_master: return False
        conn_master.autocommit = True # Necesario para consultar sys.databases
        cursor = conn_master.cursor()
        cursor.execute("SELECT COUNT(*) FROM sys.databases WHERE name = ?", (_DATABASE,))
        exists = cursor.fetchone()[0] > 0
        if exists: print(f"✅ DB '{_DATABASE}' ya existe.")
        else: print(f"ℹ️  DB '{_DATABASE}' no existe.")
        return exists
    except Exception as e:
        print(f"❌ Error verificando DB '{_DATABASE}': {e}")
        return False
    finally:
        if conn_master: conn_master.close()

def create_database():
    # Intenta crear la BD principal conectándose a 'master'
    print(f"--- Intentando crear DB '{_DATABASE}' ---")
    conn_master = None
    try:
        conn_master = get_connection('master')
        if not conn_master: return False
        conn_master.autocommit = True # Necesario para CREATE DATABASE
        cursor = conn_master.cursor()
        cursor.execute(f"CREATE DATABASE [{_DATABASE}]") # Crea la BD con el nombre actual
        print(f"✅ DB '{_DATABASE}' creada.")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Error crítico al crear DB '{_DATABASE}': {e}")
        print("   Verifica permisos 'dbcreator'.")
        return False
    finally:
        if conn_master: conn_master.close()

def check_schema_exists(conn):
    # Verifica si la tabla 'Roles' existe dentro de la conexión dada
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'Roles'")
        exists = cursor.fetchone()[0] > 0
        return exists
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def initialize_database_schema():
    # Flujo completo: Verifica/Crea BD -> Verifica/Crea Tablas (schema)
    print("--- Iniciando inicialización DB ---")
    if not check_database_exists(): # Si la BD no existe...
        if not create_database(): return False # ...intenta crearla, si falla, termina.

    # Ahora la BD (_DATABASE) debería existir, conectamos a ella
    conn = get_connection(_DATABASE)
    if not conn:
        print(f"❌ No se pudo conectar a '{_DATABASE}' para crear schema.")
        return False

    # Verifica si las tablas ya existen dentro de _DATABASE
    if check_schema_exists(conn):
        print("✅ Esquema (tablas) ya existe.")
        conn.close(); return True # Ya está todo listo

    # Si las tablas no existen, las crea
    print("ℹ️  Esquema (tablas) no existe. Creando...")
    try:
        cursor = conn.cursor()
        sql_script = """
        CREATE TABLE Roles ( idRol INT IDENTITY(1,1) PRIMARY KEY, NombreRol NVARCHAR(50) NOT NULL UNIQUE );
        CREATE TABLE Usuarios ( idUsuario INT IDENTITY(1,1) PRIMARY KEY, NombreUsuario NVARCHAR(100) NOT NULL UNIQUE, NombreCompleto NVARCHAR(200) NOT NULL, Contrasena VARBINARY(60) NOT NULL, idRol INT NOT NULL, Activo BIT NOT NULL DEFAULT 1, CONSTRAINT FK_Usuarios_Roles FOREIGN KEY (idRol) REFERENCES Roles(idRol) );
        CREATE TABLE Categorias ( idCategoria INT IDENTITY(1,1) PRIMARY KEY, NombreCategoria NVARCHAR(100) NOT NULL UNIQUE );
        CREATE TABLE Productos ( idProducto INT IDENTITY(1,1) PRIMARY KEY, Codigo NVARCHAR(50) NOT NULL UNIQUE, CodigoBarra NVARCHAR(50) NULL UNIQUE, NombreProducto NVARCHAR(200) NOT NULL UNIQUE, idCategoria INT NOT NULL, Precio DECIMAL(10, 2) NOT NULL, Stock INT NOT NULL DEFAULT 0, Activo BIT NOT NULL DEFAULT 1, CONSTRAINT FK_Productos_Categorias FOREIGN KEY (idCategoria) REFERENCES Categorias(idCategoria) );
        CREATE TABLE Cajas ( idCaja INT IDENTITY(1,1) PRIMARY KEY, FechaCaja DATE NOT NULL, Turno NVARCHAR(50) NOT NULL DEFAULT 'General', idUsuarioApertura INT NOT NULL, FechaHoraApertura DATETIME NOT NULL DEFAULT GETDATE(), idUsuarioCierre INT NULL, FechaHoraCierre DATETIME NULL, Estado NVARCHAR(20) NOT NULL DEFAULT 'Abierta', TotalVentas DECIMAL(10, 2) NULL, TotalGastos DECIMAL(10, 2) NULL, BalanceNeto DECIMAL(10, 2) NULL, CONSTRAINT FK_Cajas_UsuarioApertura FOREIGN KEY (idUsuarioApertura) REFERENCES Usuarios(idUsuario), CONSTRAINT FK_Cajas_UsuarioCierre FOREIGN KEY (idUsuarioCierre) REFERENCES Usuarios(idUsuario) );
        CREATE TABLE Ventas ( idVenta INT IDENTITY(1,1) PRIMARY KEY, idCaja INT NOT NULL, idUsuario INT NOT NULL, Total DECIMAL(10, 2) NOT NULL, idMetodoPago INT NULL, FechaVenta DATETIME NOT NULL DEFAULT GETDATE(), CONSTRAINT FK_Ventas_Caja FOREIGN KEY (idCaja) REFERENCES Cajas(idCaja), CONSTRAINT FK_Ventas_Usuarios FOREIGN KEY (idUsuario) REFERENCES Usuarios(idUsuario) );
        CREATE TABLE DetalleVentas ( idDetalleVenta INT IDENTITY(1,1) PRIMARY KEY, idVenta INT NOT NULL, idProducto INT NOT NULL, Cantidad INT NOT NULL, PrecioUnitario DECIMAL(10, 2) NOT NULL, CONSTRAINT FK_DetalleVentas_Ventas FOREIGN KEY (idVenta) REFERENCES Ventas(idVenta), CONSTRAINT FK_DetalleVentas_Productos FOREIGN KEY (idProducto) REFERENCES Productos(idProducto) );
        CREATE TABLE Gastos ( idGasto INT IDENTITY(1,1) PRIMARY KEY, Descripcion NVARCHAR(255) NOT NULL, Monto DECIMAL(10, 2) NOT NULL, Categoria NVARCHAR(100) NULL, Nota NVARCHAR(500) NULL, FechaGasto DATE NOT NULL DEFAULT GETDATE() );
        CREATE TABLE MetodosPago (idMetodoPago INT IDENTITY(1,1) PRIMARY KEY, Nombre NVARCHAR(100) NOT NULL UNIQUE, TipoMetodo NVARCHAR(50) NOT NULL DEFAULT 'Otros', Activo BIT NOT NULL DEFAULT 1);
        CREATE TABLE CierresDeCaja (idCierre INT IDENTITY(1,1) PRIMARY KEY, FechaCierre DATE NOT NULL UNIQUE, TotalVentas DECIMAL(10, 2) NOT NULL, TotalGastos DECIMAL(10, 2) NOT NULL, BalanceNeto DECIMAL(10, 2) NOT NULL, idUsuarioCierre INT NOT NULL, FechaRegistro DATETIME NOT NULL DEFAULT GETDATE(), CONSTRAINT FK_Cierres_Usuarios FOREIGN KEY (idUsuarioCierre) REFERENCES Usuarios(idUsuario));
        CREATE TABLE CierresDeCajaDetalle (idCierreDetalle INT IDENTITY(1,1) PRIMARY KEY, idCierre INT NOT NULL, idMetodoPago INT NOT NULL, Total DECIMAL(10, 2) NOT NULL, CONSTRAINT FK_CierreDetalle_Cierre FOREIGN KEY (idCierre) REFERENCES CierresDeCaja(idCierre), CONSTRAINT FK_CierreDetalle_Metodo FOREIGN KEY (idMetodoPago) REFERENCES MetodosPago(idMetodoPago));
        CREATE TABLE Configuracion ( idConfig INT IDENTITY(1,1) PRIMARY KEY, NombreNegocio NVARCHAR(200) NULL, TipoNegocio NVARCHAR(100) NULL, UsarCodigosBarra BIT NOT NULL DEFAULT 0, SetupCompleto BIT NOT NULL DEFAULT 0 );
        INSERT INTO Roles (NombreRol) VALUES ('Dev'), ('Admin'), ('Usuario');
        INSERT INTO Configuracion (SetupCompleto) VALUES (0);
        INSERT INTO MetodosPago (Nombre, TipoMetodo) VALUES ('Efectivo', 'Efectivo');
INSERT INTO MetodosPago (Nombre, TipoMetodo) VALUES ('Tarjeta de Débito', 'Tarjeta');
INSERT INTO MetodosPago (Nombre, TipoMetodo) VALUES ('Tarjeta de Crédito', 'Tarjeta');
INSERT INTO MetodosPago (Nombre, TipoMetodo) VALUES ('Mercado Pago', 'Digital');
        """
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
        for command in commands:
            if command: cursor.execute(command)
        conn.commit() # Confirma creación de tablas e inserts
        print("✅ Esquema (tablas) creado.")
        return True
    except Exception as e:
        conn.rollback() # Deshace si algo falló
        print(f"❌ Error crítico al crear tablas: {e}")
        return False
    finally:
        if conn: conn.close() # Cierra conexión a _DATABASE

# --- Función de Test de Conexión (usada por el diálogo) ---
def test_connection(server, database, username=None, password=None, trusted=True):
    # Intenta conectar con los parámetros dados (normalmente a 'master' o a la BD del usuario)
    print(f"--- Probando conexión: Srv={server}, DB={database}, Trusted={trusted} ---")
    conn = None
    try:
        # Construye la cadena de prueba
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};" # Usa la BD proporcionada (ej 'master')
            f"TrustServerCertificate=yes;"
        )
        if not trusted and username and password is not None:
            conn_str += f"UID={username};PWD={password};"
        else:
            conn_str += "Trusted_Connection=yes;"
        # Intenta conectar con timeout corto y autocommit True para la prueba
        conn = pyodbc.connect(conn_str, timeout=5, autocommit=True)
        print("✅ Prueba OK.")
        return True, "Conexión exitosa."
    except Exception as e:
        print(f"❌ Prueba fallida: {e}")
        return False, f"Error de conexión:\n{e}"
    finally:
        if conn: conn.close() # Cierra la conexión de prueba

# Bloque de prueba (si ejecutas python app/database.py)
# Ya no es tan útil porque depende de set_connection_parameters
# if __name__ == '__main__': ...