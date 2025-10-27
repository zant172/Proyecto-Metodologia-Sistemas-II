from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from functools import partial
from ..auth import get_all_users, get_user_by_id, delete_user
from .user_form_dialog import UserFormDialog

class UserTableWidget(QTableWidget):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.setup_table()
    
    def setup_table(self):
        self.setColumnCount(5) # ID, Usuario, Nombre, Rol, Acciones
        self.setHorizontalHeaderLabels(['ID', 'Nombre de Usuario', 'Nombre Completo', 'Rol', 'Acciones'])
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Nombre Completo
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch) # Acciones
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setColumnHidden(0, True) # Ocultamos ID
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
    
    def load_users(self):
        users, error = get_all_users()
        if error:
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error de Base de Datos")
            msg_box.setText(f"No se pudieron cargar los usuarios:\n{error}")
            msg_box.exec()
            self.setRowCount(0)
            return
            
        self.setRowCount(len(users))
        
        for row, user in enumerate(users):
            user_id = user[0]
            
            # Columnas de datos
            self.setItem(row, 0, QTableWidgetItem(str(user_id)))
            self.setItem(row, 1, QTableWidgetItem(user[1])) # Usuario
            self.setItem(row, 2, QTableWidgetItem(user[2])) # Nombre Completo
            self.setItem(row, 3, QTableWidgetItem(user[3])) # Rol
            
            # Columna de Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(10)
            
            edit_btn = QPushButton("Editar")
            edit_btn.setObjectName("editButton")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(partial(self.parent_widget.open_edit_dialog, user_id))
            
            delete_btn = QPushButton("Eliminar")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(partial(self.parent_widget.handle_delete, user_id))
            
            actions_layout.addStretch()
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.setCellWidget(row, 4, actions_widget)

class UsersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QVBoxLayout()
        title = QLabel("Gestión de Usuarios")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Administra las cuentas del personal")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 20)
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar usuario...")
        
        add_btn = QPushButton("Agregar Usuario")
        add_btn.setObjectName("addButton")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_dialog)
        
        controls_layout.addWidget(search_input, 1)
        controls_layout.addWidget(add_btn)
        layout.addLayout(controls_layout)
        
        self.users_table = UserTableWidget(self)
        layout.addWidget(self.users_table)
        
    def refresh_data(self):
        self.users_table.load_users()

    def open_add_dialog(self):
        dialog = UserFormDialog(on_success=self.refresh_data, parent=self)
        dialog.exec()
    
    def open_edit_dialog(self, user_id):
        user_data, error = get_user_by_id(user_id)
        if error or not user_data:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"No se pudieron cargar los datos del usuario: {error}")
            msg_box.exec()
            return
        
        dialog = UserFormDialog(user_id=user_id, user_data=user_data, on_success=self.refresh_data, parent=self)
        dialog.exec()

    def handle_delete(self, user_id):
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar a este usuario?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = delete_user(user_id)
            msg_box = QMessageBox(self)
            if success:
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("Éxito")
            else:
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("Error")
            msg_box.setText(message)
            msg_box.exec()
            if success:
                self.refresh_data()