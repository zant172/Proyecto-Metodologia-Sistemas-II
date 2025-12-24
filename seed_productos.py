"""
Script de seed para cargar productos de prueba
Uso: python seed_productos.py

Este script carga productos de ejemplo para demostración.
Para limpiar los datos después, puedes ejecutar las queries de limpieza al final.
"""

import pyodbc
import json

def cargar_seed():
    # Leer configuración de conexión
    try:
        with open('connection_data.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró connection_data.json")
        print("Por favor, ejecuta la aplicación primero para configurar la base de datos.")
        return
    
    # Conectar a la base de datos
    try:
        # Usar autenticación de Windows si trusted=true o si no hay credenciales
        if config.get('trusted', False) or not config.get('username'):
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"UID={config['username']};"
                f"PWD={config['password']};"
                f"TrustServerCertificate=yes;"
            )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("✅ Conexión exitosa a la base de datos")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # Primero, necesitamos obtener o crear las categorías
    categorias_map = {}
    categorias_necesarias = ["Bebidas", "Snacks", "Lácteos", "Almacén", "Panadería", "Limpieza", "Higiene", "Comida"]
    
    print("\n📋 Verificando categorías...")
    for cat_nombre in categorias_necesarias:
        cursor.execute("SELECT idCategoria FROM Categorias WHERE NombreCategoria = ?", cat_nombre)
        row = cursor.fetchone()
        if row:
            categorias_map[cat_nombre] = row[0]
            print(f"  ✅ {cat_nombre} existe (ID: {row[0]})")
        else:
            cursor.execute("INSERT INTO Categorias (NombreCategoria) VALUES (?)", cat_nombre)
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]
            categorias_map[cat_nombre] = new_id
            print(f"  ➕ {cat_nombre} creada (ID: {new_id})")
    
    # Productos de prueba para demostración (nombre, categoria, precio, stock, codigo_barra)
    productos = [
        # Bebidas con código de barra
        ("Coca Cola 2L", "Bebidas", 2500.00, 50, "7790895641015"),
        ("Pepsi 1.5L", "Bebidas", 2000.00, 40, "7790310082126"),
        ("Fanta Naranja 2L", "Bebidas", 2300.00, 35, "7790895000959"),
        ("Sprite 1.5L", "Bebidas", 2000.00, 30, "7790895001031"),
        ("Agua Mineral 2L", "Bebidas", 1500.00, 60, "7790070000156"),
        
        # Snacks con código de barra
        ("Papas Lays Clásicas 150g", "Snacks", 3500.00, 45, "7790310982297"),
        ("Doritos Nacho 160g", "Snacks", 3800.00, 38, "7790310984273"),
        ("Cheetos 100g", "Snacks", 2800.00, 42, "7790310987113"),
        ("Oreo 118g", "Snacks", 2200.00, 50, "7622210701091"),
        ("Milka Chocolate 100g", "Snacks", 4500.00, 30, "7622210421906"),
        
        # Lácteos con código de barra
        ("Leche La Serenísima 1L", "Lácteos", 1800.00, 40, "7790150007013"),
        ("Yogur Ser 190g Frutilla", "Lácteos", 1200.00, 55, "7790742000156"),
        ("Queso Cremoso 200g", "Lácteos", 3200.00, 25, "7790070002013"),
        
        # Almacén con código de barra
        ("Arroz Gallo Oro 1kg", "Almacén", 2800.00, 35, "7790070000804"),
        ("Fideos Matarazzo 500g", "Almacén", 1500.00, 40, "7790070000200"),
        ("Aceite Cocinero 900ml", "Almacén", 4200.00, 28, "7790070001504"),
        ("Azúcar Ledesma 1kg", "Almacén", 2200.00, 45, "7790070002501"),
        ("Café La Virginia 170g", "Almacén", 5800.00, 20, "7790070003006"),
        
        # Productos sin código de barra
        ("Pan Francés", "Panadería", 1500.00, 25, None),
        ("Medialunas x6", "Panadería", 3000.00, 20, None),
        ("Facturas Surtidas x6", "Panadería", 3500.00, 18, None),
        
        # Limpieza con código de barra
        ("Detergente Magistral 500ml", "Limpieza", 3200.00, 30, "7791290003015"),
        ("Lavandina Ayudín 1L", "Limpieza", 2500.00, 35, "7791290001202"),
        ("Jabón en Pan Ariel 150g", "Limpieza", 1800.00, 40, "7791293010465"),
        
        # Higiene personal con código de barra
        ("Shampoo Sedal 350ml", "Higiene", 4500.00, 25, "7791293040196"),
        ("Jabón Dove 90g", "Higiene", 2200.00, 45, "7791293028866"),
        ("Pasta Dental Colgate 70g", "Higiene", 3800.00, 30, "7891024130209"),
        ("Desodorante Rexona 150ml", "Higiene", 5200.00, 28, "7791293035659"),
        
        # Productos adicionales sin código
        ("Empanadas x12", "Comida", 6000.00, 15, None),
        ("Pizza Muzzarella Grande", "Comida", 8500.00, 10, None),
    ]
    
    print("\n📦 Insertando productos de prueba...")
    productos_insertados = 0
    
    try:
        for nombre, categoria, precio, stock, codigo_barra in productos:
            try:
                # Generar código único para el producto
                cursor.execute("SELECT MAX(idProducto) FROM Productos")
                max_id = cursor.fetchone()[0] or 0
                codigo = f"PROD{max_id + 1:04d}"
                
                id_categoria = categorias_map[categoria]
                
                cursor.execute("""
                    INSERT INTO Productos (Codigo, NombreProducto, idCategoria, Precio, Stock, CodigoBarra, Activo)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, codigo, nombre, id_categoria, precio, stock, codigo_barra)
                productos_insertados += 1
                codigo_display = codigo_barra if codigo_barra else "Sin código"
                print(f"  ✅ {nombre} - ${precio} - Stock: {stock} - Código: {codigo_display}")
            except pyodbc.IntegrityError as e:
                if "UNIQUE KEY" in str(e) or "duplicate" in str(e).lower():
                    print(f"  ⚠️  {nombre} - Ya existe (código duplicado)")
                else:
                    print(f"  ❌ {nombre} - Error: {e}")
            except Exception as e:
                print(f"  ❌ {nombre} - Error: {e}")
        
        conn.commit()
        print(f"\n✅ Seed completado: {productos_insertados} productos insertados")
        
        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) as total FROM Productos")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) as total FROM Productos WHERE CodigoBarra IS NOT NULL")
        con_codigo = cursor.fetchone()[0]
        
        print(f"\n📊 Resumen:")
        print(f"  • Total productos en BD: {total}")
        print(f"  • Productos con código de barra: {con_codigo}")
        print(f"  • Productos sin código: {total - con_codigo}")
        
        print("\n" + "="*60)
        print("Para LIMPIAR los datos de prueba después de la demo, ejecuta:")
        print("="*60)
        print("\nOpción 1 - Borrar SOLO los productos insertados por este seed:")
        print("DELETE FROM Productos WHERE Nombre IN (")
        print("  'Coca Cola 2L', 'Pepsi 1.5L', 'Fanta Naranja 2L',")
        print("  'Sprite 1.5L', 'Agua Mineral 2L', etc...")
        print(")")
        print("\nOpción 2 - Borrar TODOS los productos:")
        print("DELETE FROM DetalleVentas  -- Primero las referencias")
        print("DELETE FROM Productos      -- Luego los productos")
        print("DBCC CHECKIDENT ('Productos', RESEED, 0)  -- Reiniciar contador")
        print("\n⚠️  ADVERTENCIA: La opción 2 borra TODOS los productos!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error durante la inserción: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    print("="*60)
    print("     SEED DE PRODUCTOS DE PRUEBA - SISTEMA DE VENTAS")
    print("="*60)
    print("\nEste script insertará ~30 productos de ejemplo para demostración.")
    print("Presiona Ctrl+C para cancelar o Enter para continuar...")
    
    try:
        input()
        cargar_seed()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
