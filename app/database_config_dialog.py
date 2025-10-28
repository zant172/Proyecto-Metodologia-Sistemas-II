import sys
import pyodbc
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QComboBox, QFormLayout,
                             QStackedWidget, QWidget, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal

# Importa SOLO la función de test desde database.py
from .database import test_connection

class DatabaseConfigDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Base de Datos - SistemaGestionVntsJG")
        self.setMinimumWidth(450)
        self._connection_details = {} # Almacenará temporalmente los detalles exitosos

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        title_label = QLabel("Selecciona el Tipo de Conexión")
        title_label.setObjectName("pageTitle")
        title_label.setStyleSheet("font-size: 20px; margin-bottom: 10px; border-bottom: none;")
        self.main_layout.addWidget(title_label)

        self.radio_layout = QHBoxLayout()
        self.radio_group = QButtonGroup(self)
        self.radio_local = QRadioButton("SQL Server Local (Aut. Windows)")
        self.radio_sqlauth = QRadioButton("Azure SQL / SQL Server (Usuario/Contraseña)")
        self.radio_local.setChecked(True)
        self.radio_group.addButton(self.radio_local, 1)
        self.radio_group.addButton(self.radio_sqlauth, 2)
        self.radio_layout.addWidget(self.radio_local)
        self.radio_layout.addWidget(self.radio_sqlauth)
        self.main_layout.addLayout(self.radio_layout)

        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self._create_local_form())
        self.form_stack.addWidget(self._create_sqlauth_form())
        self.main_layout.addWidget(self.form_stack)
        self.radio_group.idClicked.connect(self.switch_form)

        self.button_layout = QHBoxLayout()
        self.test_button = QPushButton("Probar Conexión")
        self.continue_button = QPushButton("Continuar")
        self.cancel_button = QPushButton("Salir")
        self.test_button.setObjectName("editButton")
        self.continue_button.setObjectName("addButton")
        self.cancel_button.setObjectName("cancelButton")
        self.test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.test_button)
        self.button_layout.addWidget(self.continue_button)
        self.main_layout.addLayout(self.button_layout)

        self.cancel_button.clicked.connect(self.reject)
        self.test_button.clicked.connect(self.run_test_connection) # Renombrado para claridad
        # Conecta Continuar directamente a accept_if_connection_ok
        self.continue_button.clicked.connect(self.accept_if_connection_ok)

        self.switch_form(1)

    def _create_local_form(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setVerticalSpacing(10)
        self.local_server_input = QLineEdit("localhost\\SQLEXPRESS")
        db_name_label = QLabel("sistemgestionvntsjg")
        db_name_label.setStyleSheet("font-style: italic; color: #94A3B8;")
        layout.addRow("Nombre Servidor SQL:", self.local_server_input)
        layout.addRow("Nombre Base Datos:", db_name_label)
        return widget

    def _create_sqlauth_form(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setVerticalSpacing(10)
        self.sql_server_input = QLineEdit()
        self.sql_server_input.setPlaceholderText("ej: servidor.database.windows.net")
        self.sql_db_input = QLineEdit("sistemgestionvntsjg")
        self.sql_user_input = QLineEdit()
        self.sql_pass_input = QLineEdit()
        self.sql_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Servidor:", self.sql_server_input)
        layout.addRow("Base de Datos:", self.sql_db_input)
        layout.addRow("Usuario SQL:", self.sql_user_input)
        layout.addRow("Contraseña SQL:", self.sql_pass_input)
        return widget

    def switch_form(self, radio_id):
        self.form_stack.setCurrentIndex(radio_id - 1) # Índice 0 para ID 1, índice 1 para ID 2

    def get_current_details(self):
        details = {}
        is_local = self.radio_local.isChecked()
        details['trusted'] = is_local # Guarda si es trusted o no
        if is_local:
            details['server'] = self.local_server_input.text().strip()
            details['database'] = "sistemgestionvntsjg"
            details['username'] = None
            details['password'] = None
        else:
            details['server'] = self.sql_server_input.text().strip()
            details['database'] = self.sql_db_input.text().strip()
            details['username'] = self.sql_user_input.text().strip()
            details['password'] = self.sql_pass_input.text()

        error_msg = None
        if not details['server'] or not details['database']:
            error_msg = "Servidor y Base de Datos son obligatorios."
        if not details['trusted'] and (not details['username'] or details['password'] is None):
             error_msg = "Usuario y Contraseña SQL son obligatorios."

        return details, error_msg

    def run_test_connection(self):
        # Ejecuta la prueba de conexión y devuelve True/False
        details, error_msg = self.get_current_details()
        if error_msg:
            QMessageBox.warning(self, "Datos Incompletos", error_msg)
            return False

        # Llama a la función test_connection importada de database.py
        success, msg = test_connection(details['server'], 'master', # Prueba contra master
                                        details['username'], details['password'],
                                        details['trusted'])
        if success:
            QMessageBox.information(self, "Conexión Exitosa", msg)
            return True
        else:
            QMessageBox.critical(self, "Error de Conexión", msg)
            return False

    def accept_if_connection_ok(self):
        # Se llama al presionar "Continuar"
        # Primero, intenta probar la conexión
        if self.run_test_connection():
            # Si la prueba es exitosa, guarda los detalles y cierra
            details, _ = self.get_current_details()
            self._connection_details = details # Guarda internamente
            self.accept() # Cierra el diálogo con código Accepted

    def get_connection_details(self):
        # Para que main.py pueda obtener los detalles después de accept()
        return self._connection_details