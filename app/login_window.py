from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from app.main_window import MainWindow
from app.auth import verify_user

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_win = None
        
        self.setWindowTitle("InfinityTech - Inicio de Sesión")
        self.setGeometry(0, 0, 400, 500)
        self.setStyleSheet(self.get_stylesheet())

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

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor, ingrese usuario y contraseña.")
            return
            
        user_role = verify_user(username, password)
        
        if user_role:
            self.open_main_window(user_role)
        else:
            QMessageBox.warning(self, "Error de Acceso", "Usuario o contraseña incorrectos.")

    def open_main_window(self, role):
        self.main_win = MainWindow(user_role=role)
        self.main_win.show()
        self.close()

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
                color: #ecf0f1;
            }
            QWidget#container {
                background-color: #34495e;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """