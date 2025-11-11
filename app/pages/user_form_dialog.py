from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from ..auth import get_all_roles, create_user, update_user

class UserFormDialog(QDialog):
    def __init__(self, user_id=None, user_data=None, on_success=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.user_data = user_data
        self.on_success = on_success
        self.roles_map = {}

        self.setWindowTitle(f"{'Editar' if user_id else 'Agregar'} Usuario")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.username_input = QLineEdit()
        self.fullname_input = QLineEdit()
        self.role_combo = QComboBox()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Nombre de Usuario:", self.username_input)
        form_layout.addRow("Nombre Completo:", self.fullname_input)
        form_layout.addRow("Rol:", self.role_combo)
        
        if user_id:
            self.password_input.setPlaceholderText("(Dejar en blanco para no cambiar)")
            form_layout.addRow("Nueva Contraseña:", self.password_input)
        else:
            form_layout.addRow("Contraseña:", self.password_input)

        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        self.load_roles()
        if self.user_id and self.user_data:
            self.populate_form()

        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def load_roles(self):
        # Carga los roles (excluyendo 'Dev') desde la BD
        roles, error = get_all_roles()
        if error:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudieron cargar los roles: {error}")
            msg.exec()
            return
        
        self.role_combo.addItem("Seleccionar rol...", userData=None)
        for role_id, role_name in roles:
            self.roles_map[role_name] = role_id
            self.role_combo.addItem(role_name, userData=role_id)

    def populate_form(self):
        # Rellena si estamos editando
        self.username_input.setText(self.user_data.NombreUsuario)
        self.fullname_input.setText(self.user_data.NombreCompleto)
        
        # Selecciona el rol correcto
        role_id_to_find = self.user_data.idRol
        index = self.role_combo.findData(role_id_to_find, role=Qt.ItemDataRole.UserDataRole)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)

    def handle_save(self):
        username = self.username_input.text().strip()
        full_name = self.fullname_input.text().strip()
        password = self.password_input.text() # No quitamos espacios aquí (contraseñas pueden tener espacios)
        role_id = self.role_combo.currentData()

        # Validaciones mejoradas
        if not username or not full_name or not role_id:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Datos incompletos")
            msg.setText("Complete 'Usuario', 'Nombre Completo' y 'Rol'.")
            msg.exec()
            return
        
        # Validar longitud de campos
        if len(username) > 100:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Usuario muy largo")
            msg.setText("El nombre de usuario no puede exceder 100 caracteres.")
            msg.exec()
            return
            
        if len(full_name) > 200:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Nombre muy largo")
            msg.setText("El nombre completo no puede exceder 200 caracteres.")
            msg.exec()
            return
        
        # Validar caracteres especiales en username
        if any(char in username for char in ["'", '"', ";", " ", "--", "/*", "*/"]):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Caracteres inválidos")
            msg.setText("El usuario no puede contener espacios, comillas o caracteres SQL.")
            msg.exec()
            return
        
        # Validar longitud de contraseña para nuevos usuarios
        if not self.user_id and len(password) < 6:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Contraseña muy corta")
            msg.setText("La contraseña debe tener al menos 6 caracteres.")
            msg.exec()
            return

        try:
            # Llama a la lógica de crear o actualizar
            if self.user_id:
                new_password = password if password else None
                success, message = update_user(self.user_id, username, full_name, role_id, new_password)
            else:
                if not password:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Datos incompletos")
                    msg.setText("La contraseña es obligatoria para nuevos usuarios.")
                    msg.exec()
                    return
                success, message = create_user(username, password, full_name, role_id)
            
            # Muestra resultado y cierra si es exitoso
            msg = QMessageBox(self)
            if success:
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Éxito")
                msg.setText(message)
                msg.exec()
                if self.on_success:
                    self.on_success()
                self.accept()
            else:
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error al guardar")
                msg.setText(message)
                msg.exec()
        
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Ocurrió un error inesperado: {e}")
            msg.exec()