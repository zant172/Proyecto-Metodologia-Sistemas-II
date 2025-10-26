from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout)
from ..auth import get_all_roles, create_user, update_user

class UserFormDialog(QDialog):
    def __init__(self, user_id=None, user_data=None, on_success=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.user_data = user_data
        self.on_success = on_success
        self.roles_map = {}

        self.setWindowTitle(f"{'Editar' if user_id else 'Agregar'} Usuario")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

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

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.cancel_button = QPushButton("Cancelar")
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
        roles, error = get_all_roles()
        if error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los roles: {error}")
            return
        
        for role_id, role_name in roles:
            self.roles_map[role_name] = role_id
            self.role_combo.addItem(role_name)

    def populate_form(self):
        self.username_input.setText(self.user_data.NombreUsuario)
        self.fullname_input.setText(self.user_data.NombreCompleto)
        
        role_name = [name for name, id in self.roles_map.items() if id == self.user_data.idRol]
        if role_name:
            self.role_combo.setCurrentText(role_name[0])

    def handle_save(self):
        username = self.username_input.text()
        full_name = self.fullname_input.text()
        password = self.password_input.text()
        
        role_name = self.role_combo.currentText()
        role_id = self.roles_map.get(role_name)

        if not all([username, full_name, role_id]):
            QMessageBox.warning(self, "Datos incompletos", "Complete 'Usuario', 'Nombre Completo' y 'Rol'.")
            return

        try:
            if self.user_id:
                new_password = password if password else None
                success, message = update_user(self.user_id, username, full_name, role_id, new_password)
            else:
                if not password:
                    QMessageBox.warning(self, "Datos incompletos", "La contraseña es obligatoria para nuevos usuarios.")
                    return
                success, message = create_user(username, password, full_name, role_id)
            
            if success:
                QMessageBox.information(self, "Éxito", message)
                if self.on_success:
                    self.on_success()
                self.accept()
            else:
                QMessageBox.critical(self, "Error al guardar", message)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {e}")