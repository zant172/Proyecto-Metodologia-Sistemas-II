"""
Script de migración: Agregar columna Nota a tabla Gastos
"""
import pyodbc
import json
import os

CONNECTION_FILE = 'connection_data.json'

def load_connection_params():
    """Carga parámetros de conexión desde archivo JSON"""
    if os.path.exists(CONNECTION_FILE):
        try:
            with open(CONNECTION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('server'), data.get('database'), data.get('trusted', False), data.get('username'), data.get('password')
        except Exception as e:
            print(f"Error leyendo {CONNECTION_FILE}: {e}")
    return None, None, False, None, None

def get_connection():
    server, database, trusted, username, password = load_connection_params()
    if not server or not database:
        print("❌ No se pudo cargar la configuración de conexión")
        return None
    
    try:
        if trusted:
            conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes;'
        else:
            conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;'
        
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def migrate():
    """Agrega la columna Nota a la tabla Gastos si no existe"""
    print("=" * 60)
    print("🔧 MIGRACIÓN: Agregar columna Nota a tabla Gastos")
    print("=" * 60)
    
    conn = get_connection()
    if not conn:
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        print("\n1️⃣ Verificando si columna Nota ya existe...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Gastos' 
            AND COLUMN_NAME = 'Nota'
        """)
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("   ✅ La columna Nota ya existe en la tabla Gastos")
            return True
        
        print("   ⚠️  La columna Nota NO existe, procediendo a agregarla...")
        
        # Agregar la columna
        print("\n2️⃣ Agregando columna Nota NVARCHAR(500) NULL...")
        cursor.execute("""
            ALTER TABLE Gastos 
            ADD Nota NVARCHAR(500) NULL
        """)
        conn.commit()
        print("   ✅ Columna agregada exitosamente")
        
        # Verificar nuevamente
        print("\n3️⃣ Verificando que la columna fue agregada...")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Gastos' 
            AND COLUMN_NAME = 'Nota'
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"   ✅ Verificación exitosa:")
            print(f"      - Nombre: {result[0]}")
            print(f"      - Tipo: {result[1]}")
            print(f"      - Longitud: {result[2]}")
            print(f"      - Nullable: {result[3]}")
            
            print("\n" + "=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            return True
        else:
            print("   ❌ Error: No se pudo verificar la columna")
            return False
            
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        if conn:
            try:
                conn.rollback()
                print("   ⚠️  Rollback ejecutado")
            except:
                pass
        return False
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

if __name__ == "__main__":
    success = migrate()
    if success:
        print("\n🎉 Ahora puede ejecutar main_flet.py sin errores en la sección Gastos")
        exit(0)
    else:
        print("\n❌ La migración falló. Revise los errores anteriores.")
        exit(1)
