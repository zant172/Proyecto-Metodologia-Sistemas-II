import sys
import os
import json # Para leer/escribir el archivo de conexión
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt6.QtGui import QIcon
# Importa funciones clave de database y auth
from app.database import set_connection_parameters, initialize_database_schema, test_connection
from app.auth import ensure_superadmin_exists
# Importa ventanas
from app.login_window import LoginWindow
from app.database_config_dialog import DatabaseConfigDialog

# Nombre del archivo para guardar la configuración de conexión
CONNECTION_FILE = 'connection_data.json'

def load_connection_params():
    # Intenta cargar los parámetros desde el archivo JSON
    if os.path.exists(CONNECTION_FILE):
        try:
            with open(CONNECTION_FILE, 'r', encoding='utf-8') as f:
                params = json.load(f)
                # Validación básica de que tiene las claves esperadas
                if all(k in params for k in ['server', 'database']):
                    print(f"✅ Configuración de conexión cargada desde {CONNECTION_FILE}")
                    return params
                else:
                    print(f"⚠️ Archivo {CONNECTION_FILE} inválido (faltan claves).")
                    return None
        except Exception as e:
            print(f"❌ Error al leer {CONNECTION_FILE}: {e}")
            return None
    else:
        print(f"ℹ️  No se encontró {CONNECTION_FILE}. Se solicitará configuración.")
        return None

def save_connection_params(details):
    # Guarda los parámetros de conexión en el archivo JSON
    try:
        with open(CONNECTION_FILE, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=4) # Guarda con formato legible
        print(f"✅ Configuración de conexión guardada en {CONNECTION_FILE}")
    except Exception as e:
        print(f"❌ Error al guardar {CONNECTION_FILE}: {e}")
        # Muestra error al usuario si no se pudo guardar
        QMessageBox.warning(None, "Error al Guardar Configuración",
                            f"No se pudo guardar la configuración de conexión:\n{e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Gestion Ventas JG")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("JG Software")

    connection_ok = False # Flag para saber si tenemos conexión válida
    connection_details = None # Guardará los detalles de conexión

    # --- PASO 1: INTENTAR CONEXIÓN AUTOMÁTICA ---
    saved_params = load_connection_params()
    if saved_params:
        # Si encontramos parámetros guardados, los usamos y probamos
        set_connection_parameters(**saved_params)
        # Probamos conectando a 'master' que siempre debería existir si el server está ok
        success, msg = test_connection(saved_params['server'], 'master',
                                        saved_params.get('username'), saved_params.get('password'),
                                        saved_params.get('trusted', True))
        if success:
            print("✅ Conexión automática exitosa con parámetros guardados.")
            connection_ok = True
            connection_details = saved_params # Usaremos estos parámetros
        else:
            print(f"⚠️ Falló conexión automática con parámetros guardados: {msg}")
            # Borramos el archivo inválido para forzar reconfiguración
            if os.path.exists(CONNECTION_FILE):
                try: os.remove(CONNECTION_FILE)
                except Exception as e: print(f"❌ No se pudo borrar {CONNECTION_FILE} inválido: {e}")

    # --- PASO 2: MOSTRAR DIÁLOGO SI ES NECESARIO ---
    if not connection_ok:
        print("ℹ️  Mostrando diálogo de configuración de BD...")
        db_dialog = DatabaseConfigDialog()
        result = db_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Si el usuario aceptó y la conexión fue exitosa
            connection_details = db_dialog.get_connection_details()
            set_connection_parameters(**connection_details) # Establece para esta sesión
            save_connection_params(connection_details) # Guarda para futuras sesiones
            connection_ok = True # Ahora tenemos conexión OK
            print("✅ Configuración de BD establecida y guardada.")
        else:
            # Si el usuario canceló
            print("❌ Configuración de base de datos cancelada. Saliendo.")
            sys.exit(0) # Sale limpiamente

    # --- PASO 3: CONTINUAR SI LA CONEXIÓN ESTÁ OK ---
    if connection_ok:
        # Ahora que SÍ tenemos conexión, inicializamos schema y super admin
        if not initialize_database_schema():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error Crítico de Base de Datos")
            msg_box.setText("No se pudo inicializar el esquema.\nVerifique permisos o conexión.\nLa aplicación se cerrará.")
            try:
                with open("style.qss", "r", encoding="utf-8") as f: msg_box.setStyleSheet(f.read())
            except: pass
            msg_box.exec()
            sys.exit(1)

        ensure_superadmin_exists()

        # Cargar estilo QSS
        try:
            with open("style.qss", "r", encoding="utf-8") as f:
                style = f.read()
                app.setStyleSheet(style)
                print("✅ Estilo 'style.qss' cargado.")
        except FileNotFoundError: print("❌ Advertencia: No se encontró 'style.qss'.")
        except Exception as e: print(f"❌ Error al cargar 'style.qss': {e}")

        # Mostrar LoginWindow
        login_window = LoginWindow()
        login_window.show()
        sys.exit(app.exec()) # Inicia la aplicación
    else:
        # Si por alguna razón llegamos aquí sin conexión OK (no debería pasar)
        print("❌ Error inesperado: No se estableció conexión de BD. Saliendo.")
        sys.exit(1)