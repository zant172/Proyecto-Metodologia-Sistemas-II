import sys
from PyQt6.QtWidgets import QApplication
from app.login_window import LoginWindow
from app.auth import create_user

def setup_initial_users():
    print("--- Configurando usuarios iniciales ---")
    
    create_user(
        username='sprsjg26', 
        password='superadminpass', 
        full_name='Desarrollador del Sistema', 
        role_id=1
    )
    
    create_user(
        username='admin', 
        password='adminpass', 
        full_name='Dueño del Negocio', 
        role_id=2
    )

    create_user(
        username='empleado1', 
        password='emp123', 
        full_name='Juan Perez', 
        role_id=3
    )

if __name__ == '__main__':
    
    #setup_initial_users()

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())