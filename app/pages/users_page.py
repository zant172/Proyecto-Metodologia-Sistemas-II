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
        
        header_layout = QHBoxLayout()
        title = QLabel("Gestión de Usuarios")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_user_button = QPushButton("Agregar Usuario")
        self.add_user_button.setObjectName("addButton")
        header_layout.addWidget(self.add_user_button)
        layout.addLayout(header_layout)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6) 
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre Completo", "Rol", "Editar", "Eliminar"
        ])
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.user_table.setColumnWidth(0, 50)
        self.user_table.setColumnWidth(4, 70)
        self.user_table.setColumnWidth(5, 70)

        layout.addWidget(self.user_table)
        
        self.refresh_data()
        self.add_user_button.clicked.connect(self.open_add_dialog)

    def refresh_data(self):
        self.load_users()

    def load_users(self):
        users, error = get_all_users()
        
        if error:
            QMessageBox.critical(self, "Error de Base de Datos", 
                                 f"No se pudieron cargar los usuarios:\n{error}")
            self.user_table.setRowCount(0)
            return
            
        self.user_table.setRowCount(len(users))
        
        for row_idx, row_data in enumerate(users):
            user_id = row_data[0]
            
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.user_table.setItem(row_idx, col_idx, item)
            
            self.setup_table_buttons(row_idx, user_id)

    def setup_table_buttons(self, row, user_id):
        edit_button = QPushButton("Editar")
        edit_button.setObjectName("editButton")
        edit_button.clicked.connect(partial(self.open_edit_dialog, user_id))
        self.user_table.setCellWidget(row, 4, edit_button) 

        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(partial(self.handle_delete, user_id))
        self.user_table.setCellWidget(row, 5, delete_button)

    def open_add_dialog(self):
        dialog = UserFormDialog(on_success=self.refresh_data, parent=self)
        dialog.exec()

    def open_edit_dialog(self, user_id):
        user_data, error = get_user_by_id(user_id)
        if error or not user_data:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos del usuario: {error}")
            return
        
        dialog = UserFormDialog(user_id=user_id, user_data=user_data, on_success=self.refresh_data, parent=self)
        dialog.exec()

    def handle_delete(self, user_id):
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar a este usuario?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = delete_user(user_id)
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", message)