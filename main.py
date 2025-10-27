import sys
from PyQt6.QtWidgets import QApplication
from app.login_window import LoginWindow
from app.auth import ensure_superadmin_exists

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    app.setApplicationName("InfinityTech Gestión")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("InfinityTech")
    
    ensure_superadmin_exists()
    
    try:
        with open("style.qss", "r", encoding="utf-8") as f:
            style = f.read()
            app.setStyleSheet(style)
            print("✅ Estilo 'style.qss' cargado correctamente.")
    except FileNotFoundError:
        print("❌ Advertencia: No se encontró el archivo 'style.qss'.")
    except Exception as e:
        print(f"❌ Error al cargar 'style.qss': {e}")
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())