from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .main_window import MainWindow
from .auth import verify_user

class LoginWindow(QWidget):
    
    current_user_id = None
    
    def __init__(self):
        super().__init__()
        self.main_win = None
        
        self.setWindowTitle("InfinityTech - Inicio de Sesión")
        self.setGeometry(0, 0, 400, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container = QWidget()
        container.setFixedSize(350, 400)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.setObjectName("container")

        title = QLabel("INICIO DE SESIÓN")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.username_input = QLineEdit(placeholderText="Nombre de usuario")
        self.password_input = QLineEdit(placeholderText="Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("Ingresar")
        
        container_layout.addWidget(title)
        container_layout.addStretch()
        container_layout.addWidget(QLabel("Usuario"))
        container_layout.addWidget(self.username_input)
        container_layout.addWidget(QLabel("Contraseña"))
        container_layout.addWidget(self.password_input)
        container_layout.addStretch()
        container_layout.addWidget(self.login_button)

        main_layout.addWidget(container)
        
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor, ingrese usuario y contraseña.")
            return
            
        user_role, user_id = verify_user(username, password)
        
        if user_role and user_id:
            LoginWindow.current_user_id = user_id
            self.open_main_window(user_role, user_id)
        else:
            QMessageBox.warning(self, "Error de Acceso", "Usuario o contraseña incorrectos.")

    def open_main_window(self, role, user_id):
        self.main_win = MainWindow(user_role=role, user_id=user_id)
        self.main_win.show()
        self.close()