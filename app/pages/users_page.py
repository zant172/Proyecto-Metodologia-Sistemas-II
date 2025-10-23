from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QAbstractItemView)
from functools import partial
from ..auth import get_all_users, get_user_by_id, delete_user
from .user_form_dialog import UserFormDialog

class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # --- Cabecera ---
        header_layout = QHBoxLayout()
        title = QLabel("Gestión de Usuarios")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_user_button = QPushButton("Agregar Usuario")
        self.add_user_button.setObjectName("addButton") # Estilo verde
        header_layout.addWidget(self.add_user_button)
        layout.addLayout(header_layout)

        # --- Tabla de Usuarios ---
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6) 
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre Completo", "Rol", "Editar", "Eliminar"
        ])
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Ajustar el tamaño de las columnas
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Nombre Completo
        self.user_table.setColumnWidth(0, 50)  # ID
        self.user_table.setColumnWidth(4, 70)  # Editar
        self.user_table.setColumnWidth(5, 70)  # Eliminar

        layout.addWidget(self.user_table)
        
        # --- Carga inicial y conexiones ---
        self.load_users()
        self.add_user_button.clicked.connect(self.open_add_dialog)

    def load_users(self):
        """Carga y recarga los datos de la tabla de usuarios."""
        users, error = get_all_users()
        
        if error:
            QMessageBox.critical(self, "Error de Base de Datos", 
                                 f"No se pudieron cargar los usuarios:\n{error}")
            self.user_table.setRowCount(0)
            return
            
        self.user_table.setRowCount(len(users))
        
        for row_idx, row_data in enumerate(users):
            # row_data = (idUsuario, NombreUsuario, NombreCompleto, NombreRol)
            user_id = row_data[0]
            
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.user_table.setItem(row_idx, col_idx, item)
            
            # Añadir botones de "Editar" y "Eliminar"
            self.setup_table_buttons(row_idx, user_id)

    def setup_table_buttons(self, row, user_id):
        # Botón Editar
        edit_button = QPushButton("Editar")
        edit_button.setObjectName("editButton")
        edit_button.clicked.connect(partial(self.open_edit_dialog, user_id))
        self.user_table.setCellWidget(row, 4, edit_button) 

        # Botón Eliminar
        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(partial(self.handle_delete, user_id))
        self.user_table.setCellWidget(row, 5, delete_button)

    def refresh_table(self):
        """Función de callback para recargar la tabla."""
        self.load_users()

    def open_add_dialog(self):
        """Abre el formulario para crear un nuevo usuario."""
        dialog = UserFormDialog(on_success=self.refresh_table, parent=self)
        dialog.exec()

    def open_edit_dialog(self, user_id):
        """Abre el formulario para editar un usuario."""
        user_data, error = get_user_by_id(user_id)
        if error or not user_data:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos del usuario: {error}")
            return
        
        # user_data = (NombreUsuario, NombreCompleto, idRol)
        dialog = UserFormDialog(user_id=user_id, user_data=user_data, on_success=self.refresh_table, parent=self)
        dialog.exec()

    def handle_delete(self, user_id):
        """Maneja la lógica de borrado lógico para usuarios."""
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar a este usuario?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = delete_user(user_id)
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.refresh_table()
            else:
                QMessageBox.critical(self, "Error", message)