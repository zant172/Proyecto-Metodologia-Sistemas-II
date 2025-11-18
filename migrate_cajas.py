"""
Script de migración para agregar la tabla Cajas y actualizar Ventas
Este script agrega la funcionalidad de Caja Diaria al sistema existente
"""
import pyodbc
import json
import os
from datetime import datetime

def load_connection_config():
    config_file = "connection_data.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            data = json.load(f)
            return data
    return None

def get_connection():
    config = load_connection_config()
    if not config:
        print("❌ No se encontró configuración de conexión")
        return None
    
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"TrustServerCertificate=yes;"
    )
    
    if config.get('trusted', True):
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={config.get('username', '')};PWD={config.get('password', '')};"
    
    try:
        return pyodbc.connect(conn_str, autocommit=False)
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    print("="*60)
    print("MIGRACIÓN: Agregar tabla Cajas y actualizar Ventas")
    print("="*60)
    
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 1. Verificar si la tabla Cajas ya existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'Cajas'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("✅ La tabla Cajas ya existe")
        else:
            print("📋 Creando tabla Cajas...")
            cursor.execute("""
                CREATE TABLE Cajas (
                    idCaja INT IDENTITY(1,1) PRIMARY KEY,
                    FechaCaja DATE NOT NULL,
                    Turno NVARCHAR(50) NOT NULL DEFAULT 'General',
                    idUsuarioApertura INT NOT NULL,
                    FechaHoraApertura DATETIME NOT NULL DEFAULT GETDATE(),
                    idUsuarioCierre INT NULL,
                    FechaHoraCierre DATETIME NULL,
                    Estado NVARCHAR(20) NOT NULL DEFAULT 'Abierta',
                    TotalVentas DECIMAL(10, 2) NULL,
                    TotalGastos DECIMAL(10, 2) NULL,
                    BalanceNeto DECIMAL(10, 2) NULL,
                    CONSTRAINT FK_Cajas_UsuarioApertura FOREIGN KEY (idUsuarioApertura) REFERENCES Usuarios(idUsuario),
                    CONSTRAINT FK_Cajas_UsuarioCierre FOREIGN KEY (idUsuarioCierre) REFERENCES Usuarios(idUsuario)
                )
            """)
            print("✅ Tabla Cajas creada exitosamente")
        
        # 2. Verificar si Ventas tiene la columna idCaja
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Ventas' AND COLUMN_NAME = 'idCaja'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("✅ La columna idCaja ya existe en Ventas")
        else:
            print("📋 Verificando ventas existentes...")
            cursor.execute("SELECT COUNT(*) FROM Ventas")
            ventas_count = cursor.fetchone()[0]
            
            if ventas_count > 0:
                print(f"⚠️  Existen {ventas_count} ventas sin idCaja")
                print("📋 Creando caja retroactiva para ventas existentes...")
                
                # Crear una caja cerrada retroactiva para las ventas existentes
                cursor.execute("SELECT MIN(idUsuario) FROM Usuarios WHERE Activo = 1")
                primer_usuario = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO Cajas (FechaCaja, Turno, idUsuarioApertura, FechaHoraApertura, 
                                       idUsuarioCierre, FechaHoraCierre, Estado)
                    VALUES (?, 'General', ?, ?, ?, ?, 'Cerrada')
                """, (
                    datetime.now().date(),
                    primer_usuario,
                    datetime.now(),
                    primer_usuario,
                    datetime.now()
                ))
                
                cursor.execute("SELECT @@IDENTITY")
                caja_retroactiva_id = cursor.fetchone()[0]
                print(f"✅ Caja retroactiva creada (ID: {caja_retroactiva_id})")
            
            print("📋 Agregando columna idCaja a Ventas...")
            cursor.execute("""
                ALTER TABLE Ventas 
                ADD idCaja INT NULL
            """)
            
            if ventas_count > 0:
                print(f"📋 Asignando ventas existentes a caja retroactiva...")
                cursor.execute(f"""
                    UPDATE Ventas 
                    SET idCaja = {caja_retroactiva_id}
                    WHERE idCaja IS NULL
                """)
                print(f"✅ {ventas_count} ventas actualizadas")
            
            print("📋 Haciendo idCaja obligatorio y agregando foreign key...")
            cursor.execute("""
                ALTER TABLE Ventas 
                ALTER COLUMN idCaja INT NOT NULL
            """)
            
            cursor.execute("""
                ALTER TABLE Ventas
                ADD CONSTRAINT FK_Ventas_Caja FOREIGN KEY (idCaja) REFERENCES Cajas(idCaja)
            """)
            
            print("✅ Columna idCaja agregada y configurada en Ventas")
        
        conn.commit()
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\nAhora puedes usar la funcionalidad de Caja Diaria:")
        print("  1. Abre una caja desde '💵 Caja Diaria'")
        print("  2. Registra ventas en '💳 Punto de Venta'")
        print("  3. Cierra la caja al finalizar el turno")
        print("  4. Consulta el historial en '📊 Reportes'\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR EN LA MIGRACIÓN: {e}")
        print("   La base de datos no fue modificada.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
