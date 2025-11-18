"""
Script de migración: Agregar soporte para códigos de barra
Agrega la columna CodigoBarra a la tabla Productos y UsarCodigosBarra a Configuracion
"""

import json
import pyodbc

def get_connection():
    try:
        with open('connection_data.json', 'r') as f:
            config = json.load(f)
        
        server = config.get('server', 'localhost\\SQLEXPRESS')
        database = config.get('database', 'sistemgestionvntsjg')
        trusted = config.get('trusted_connection', True)
        
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection={'yes' if trusted else 'no'};"
            f"TrustServerCertificate=yes;"
        )
        
        return pyodbc.connect(conn_str, timeout=10)
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def migrate():
    print("=" * 60)
    print("🔄 MIGRACIÓN: Agregar soporte para códigos de barra")
    print("=" * 60)
    
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Verificar y agregar columna CodigoBarra a Productos
        print("\n1️⃣  Verificando columna CodigoBarra en tabla Productos...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Productos' AND COLUMN_NAME = 'CodigoBarra'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("   ➕ Agregando columna CodigoBarra...")
            cursor.execute("""
                ALTER TABLE Productos 
                ADD CodigoBarra NVARCHAR(50) NULL
            """)
            print("   ✅ Columna CodigoBarra agregada")
            
            # Agregar constraint UNIQUE
            try:
                cursor.execute("""
                    ALTER TABLE Productos 
                    ADD CONSTRAINT UQ_Productos_CodigoBarra UNIQUE (CodigoBarra)
                """)
                print("   ✅ Constraint UNIQUE agregado a CodigoBarra")
            except:
                print("   ⚠️  Constraint UNIQUE ya existe o no se pudo agregar")
        else:
            print("   ℹ️  Columna CodigoBarra ya existe")
        
        # 2. Verificar y agregar columna UsarCodigosBarra a Configuracion
        print("\n2️⃣  Verificando columna UsarCodigosBarra en tabla Configuracion...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Configuracion' AND COLUMN_NAME = 'UsarCodigosBarra'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("   ➕ Agregando columna UsarCodigosBarra...")
            cursor.execute("""
                ALTER TABLE Configuracion 
                ADD UsarCodigosBarra BIT NOT NULL DEFAULT 0
            """)
            print("   ✅ Columna UsarCodigosBarra agregada (por defecto: desactivado)")
        else:
            print("   ℹ️  Columna UsarCodigosBarra ya existe")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\n📋 INSTRUCCIONES:")
        print("   1. Si deseas usar códigos de barra, actualiza manualmente:")
        print("      UPDATE Configuracion SET UsarCodigosBarra = 1")
        print("   2. Ahora puedes agregar códigos de barra a tus productos")
        print("   3. El punto de venta detectará automáticamente códigos escaneados")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
