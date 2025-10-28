import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from app.database import initialize_database_schema
from app.login_window import LoginWindow
from app.auth import ensure_superadmin_exists

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("InfinityTech Gestión")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("InfinityTech")

    # Opcional: Icono
    # icon_path = os.path.join(os.path.dirname(__file__), 'app', 'icons', 'app_icon.ico')
    # if os.path.exists(icon_path): app.setWindowIcon(QIcon(icon_path))

    if not initialize_database_schema():
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error Crítico de Base de Datos")
        msg_box.setText("No se pudo inicializar el esquema.\nVerifique config.ini y permisos.\nLa aplicación se cerrará.")
        try:
            # Intenta aplicar estilo al mensaje de error
            with open("style.qss", "r", encoding="utf-8") as f:
                msg_box.setStyleSheet(f.read())
        except: pass # Ignora si no puede cargar estilo aquí
        msg_box.exec()
        sys.exit(1)

    # Crea el super admin si no existe, después de asegurar las tablas
    ensure_superadmin_exists()

    # Carga el estilo principal de la aplicación
    try:
        with open("style.qss", "r", encoding="utf-8") as f:
            style = f.read()
            app.setStyleSheet(style)
            print("✅ Estilo 'style.qss' cargado.")
    except FileNotFoundError:
        print("❌ Advertencia: No se encontró 'style.qss'.")
    except Exception as e:
        print(f"❌ Error al cargar 'style.qss': {e}")

    # Inicia la ventana de login
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())