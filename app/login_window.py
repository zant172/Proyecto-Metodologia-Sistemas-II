import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QHBoxLayout, QFrame, QApplication, QDialog)
from PyQt6.QtGui import QFont # Importado por si acaso, aunque QSS maneja fuentes
from PyQt6.QtCore import Qt
from .main_window import MainWindow # Necesita MainWindow para abrirla
from .auth import verify_user, is_initial_setup_complete # Funciones de lógica
# Intenta importar el asistente, si falla, deshabilita esa parte del flujo
try:
    from .pages.setup_window import SettingsG_Windows
    SETUP_WINDOW_AVAILABLE = True
except ImportError:
    print("⚠️ Advertencia: No se encontró 'app/pages/setup_window.py'. El asistente no estará disponible.")
    SETUP_WINDOW_AVAILABLE = False
    SettingsG_Windows = None # Define como None para evitar errores

class LoginWindow(QWidget):
    current_user_id = None # Podría usarse en MainWindow si se necesita

    def __init__(self):
        super().__init__()
        self.main_win = None # Guardará la referencia a MainWindow
        self.setWindowTitle("InfinityTech - Inicio de Sesión")
        self.setFixedSize(450, 550) # Tamaño fijo para consistencia

        # Centrar la ventana al iniciar
        screen_geo = self.screen().availableGeometry()
        self.move(int((screen_geo.width() - self.width()) / 2),
                  int((screen_geo.height() - self.height()) / 2))

        # Layout principal que centrará el contenedor
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Contenedor principal con estilo aplicado por QSS (#container)
        container = QFrame()
        container.setObjectName("container") # ID para QSS
        container.setFixedSize(380, 450) # Tamaño fijo del contenedor interior
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40) # Padding

        # Título y subtítulo
        title = QLabel("INICIO DE SESIÓN")
        title.setObjectName("title") # ID para QSS
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Accede al Sistema de Gestión")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # El estilo de subtitle viene del QSS general de QLabel dentro de #container

        # Campos de entrada (estilo aplicado por QSS general)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Oculta texto

        # Botón de Ingresar (estilo por QSS general de QPushButton)
        self.login_button = QPushButton("Ingresar")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor) # Cambia cursor

        # Añadir widgets al layout del contenedor con espaciadores
        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addStretch(1) # Espacio flexible
        container_layout.addWidget(QLabel("Usuario:")) # Label simple, estilo QSS
        container_layout.addWidget(self.username_input)
        container_layout.addWidget(QLabel("Contraseña:")) # Label simple, estilo QSS
        container_layout.addWidget(self.password_input)
        container_layout.addStretch(1)
        container_layout.addWidget(self.login_button)
        container_layout.addStretch(1)

        # Establecer layout del contenedor (importante!)
        container.setLayout(container_layout)
        # Añadir contenedor al layout principal de la ventana
        main_layout.addWidget(container)

        # Conectar señales: clic en botón o Enter en contraseña
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        # Se activa al intentar iniciar sesión
        username = self.username_input.text().strip() # Quita espacios extra
        password = self.password_input.text() # La contraseña puede tener espacios

        # Validación simple
        if not username or not password:
            QMessageBox.warning(self, "Campos Vacíos", "Ingrese usuario y contraseña.")
            return

        # Llama a la lógica de verificación en auth.py
        user_role, user_id = verify_user(username, password)

        if user_role and user_id: # Si las credenciales son válidas
            LoginWindow.current_user_id = user_id # Guarda ID
            # Llama a la función que decide si mostrar asistente o MainWindow
            self.open_main_window(user_role, user_id)
        else: # Si las credenciales son inválidas
            QMessageBox.warning(self, "Error de Acceso", "Usuario o contraseña incorrectos.")
            self.password_input.clear() # Limpia solo contraseña para reintentar

    def open_main_window(self, role, user_id):
        # Punto clave: Decide qué ventana abrir después del login exitoso
        # Condición 1: Es el Super Admin ('Dev')?
        # Condición 2: ¿El asistente de setup está disponible (archivo existe)?
        # Condición 3: ¿El setup inicial NO está completo (is_initial_setup_complete devuelve False)?
        if role == 'Dev' and SETUP_WINDOW_AVAILABLE and not is_initial_setup_complete():
            # Si se cumplen las 3 condiciones -> Muestra el asistente
            print("Lanzando asistente de configuración inicial...")
            setup_dialog = SettingsG_Windows(self) # Crea instancia del asistente
            result = setup_dialog.exec() # Muestra modalmente (bloquea login)

            if result == QDialog.DialogCode.Accepted: # Si el asistente se completó bien
                print("Asistente completado. Abriendo MainWindow...")
                self.main_win = MainWindow(user_role=role, user_id=user_id) # Crea MainWindow
                self.main_win.show() # Muestra MainWindow
                self.close() # Cierra LoginWindow
            else: # Si el asistente se cerró/canceló
                print("Asistente cancelado o cerrado.")
                QMessageBox.information(self, "Configuración Pendiente",
                                        "La configuración inicial es necesaria.\nLa aplicación se cerrará.")
                # Cierra toda la aplicación
                instance = QApplication.instance()
                if instance: instance.quit()
                else: sys.exit() # Salida alternativa

        else:
            # Si NO es Dev, O el asistente no existe, O el setup YA está completo
            # Protección extra: Si NO es Dev pero el setup está incompleto (no debería pasar)
            if not is_initial_setup_complete() and role != 'Dev':
                 QMessageBox.critical(self, "Configuración Incompleta",
                                       "Configuración inicial incompleta.\nContacta al Super Admin.")
                 self.username_input.clear() # Limpia campos y se queda en login
                 self.password_input.clear()
            else:
                # Caso normal: Abre MainWindow directamente
                print("Abriendo MainWindow directamente...")
                self.main_win = MainWindow(user_role=role, user_id=user_id)
                self.main_win.show()
                self.close() # Cierra LoginWindow