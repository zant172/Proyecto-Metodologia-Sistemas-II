"""
Script para crear el ejecutable del Sistema de Gestión de Ventas SJG
Usa PyInstaller para empaquetar la aplicación
"""

import PyInstaller.__main__
import os

# Obtener el directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Argumentos para PyInstaller
PyInstaller.__main__.run([
    'main.py',                          # Archivo principal
    '--name=SistemaVentasSJG',          # Nombre del ejecutable
    '--onefile',                        # Un solo archivo
    '--windowed',                       # Sin consola (GUI)
    '--icon=NONE',                      # Sin ícono por ahora
    
    # Agregar datos necesarios
    f'--add-data={os.path.join(current_dir, "connection_data.json")}{os.pathsep}.',
    f'--add-data={os.path.join(current_dir, "app")}{os.pathsep}app',
    
    # Opciones adicionales
    '--noconfirm',                      # No pedir confirmación
    '--clean',                          # Limpiar archivos temporales
    
    # Hooks ocultos para dependencias
    '--hidden-import=flet',
    '--hidden-import=pyodbc',
    '--hidden-import=decimal',
    '--hidden-import=datetime',
    
    # Optimizaciones
    '--optimize=2',                     # Optimizar bytecode
])

print("\n" + "="*60)
print("✅ Ejecutable creado exitosamente!")
print("="*60)
print(f"\n📁 Ubicación: {os.path.join(current_dir, 'dist', 'SistemaVentasSJG.exe')}")
print("\n📝 IMPORTANTE:")
print("   1. El ejecutable está en la carpeta 'dist'")
print("   2. Necesitas SQL Server instalado en el PC donde se ejecute")
print("   3. Necesitas ODBC Driver 18 for SQL Server")
print("   4. La primera ejecución puede tardar un poco")
print("\n💡 Para distribuir:")
print("   - Copia el archivo .exe")
print("   - Asegúrate que las PCs tengan SQL Server y ODBC Driver")
print("="*60 + "\n")
