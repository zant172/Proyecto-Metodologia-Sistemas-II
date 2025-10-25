from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt

from .main_window import MainWindow
from .auth import verify_user

class LoginWindow(QWidget):
    current_user_id = None
    def __init__(self):
        super().__init__()
        self.main_win = None
        self.setObjectName("loginWindow")
        self.setWindowTitle("InfinityTech - Inicio de Sesión")
        # Ajusta el tamaño inicial si es necesario, o deja que el layout lo controle
        # self.setGeometry(0, 0, 450, 600) # Ejemplo

        # Layout principal para centrar el contenedor
        main_layout = QVBoxLayout(self)
        main_layout.addStretch(1) # Empuja hacia el centro verticalmente

        container = QWidget()
        container.setObjectName("loginContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30) # Padding interno
        container_layout.setSpacing(15) # Espacio entre widgets

        title = QLabel("INICIO DE SESIÓN")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Campo Usuario
        user_label = QLabel("Usuario")
        user_label.setObjectName("loginLabel")
        self.username_input = QLineEdit()
        self.username_input.setObjectName("loginInput")
        self.username_input.setPlaceholderText("Ingrese su nombre de usuario")

        # Campo Contraseña
        pass_label = QLabel("Contraseña")
        pass_label.setObjectName("loginLabel")
        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Botón Ingresar
        self.login_button = QPushButton("Ingresar")
        self.login_button.setObjectName("loginButton")
        # Establece una política de tamaño preferida para el botón
        self.login_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


        # Añadir widgets al layout del contenedor
        container_layout.addWidget(title)
        # container_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)) # Espaciador opcional
        container_layout.addWidget(user_label)
        container_layout.addWidget(self.username_input)
        container_layout.addWidget(pass_label)
        container_layout.addWidget(self.password_input)
        container_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)) # Pequeño espacio antes del botón
        container_layout.addWidget(self.login_button)
        # container_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)) # Espaciador opcional

        # Añadir contenedor al layout principal
        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter) # Centra horizontalmente
        main_layout.addStretch(1) # Empuja hacia el centro verticalmente


        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        # Ajusta el tamaño de la ventana al contenido si no se especificó geometría
        # self.adjustSize()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, ingrese usuario y contraseña.")
            return

        user_role, user_id = verify_user(username, password)

        if user_role and user_id:
            LoginWindow.current_user_id = user_id
            self.open_main_window(user_role, user_id)
        else:
            QMessageBox.critical(self, "Error de Acceso", "Usuario o contraseña incorrectos.")
            self.password_input.clear() # Limpia solo la contraseña

    def open_main_window(self, role, user_id):
        self.main_win = MainWindow(user_role=role, user_id=user_id)
        self.main_win.show()
        self.close()