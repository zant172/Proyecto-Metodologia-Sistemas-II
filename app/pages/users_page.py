from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
from functools import partial
from ..auth import get_all_users, get_user_by_id, delete_user
from .user_form_dialog import UserFormDialog

class UsersPage(QWidget):
    def __init__(self):
        super().__init__(); layout = QVBoxLayout(self); header_layout = QHBoxLayout()
        title = QLabel("Gestión de Usuarios"); title.setObjectName("pageTitle"); header_layout.addWidget(title); header_layout.addStretch()
        self.add_button = QPushButton("Agregar Usuario"); self.add_button.setObjectName("addButton"); header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        self.table = QTableWidget(); self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre Completo", "Rol", "Editar", "Eliminar"])
        self.table.verticalHeader().setVisible(False); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 50); self.table.setColumnWidth(4, 70); self.table.setColumnWidth(5, 70)
        layout.addWidget(self.table); self.refresh_data(); self.add_button.clicked.connect(self.open_add_dialog)

    def refresh_data(self): self.load_users()

    def load_users(self):
        users, error = get_all_users()
        if error: QMessageBox.critical(self, "Error DB", f"No se cargaron usuarios:\n{error}"); self.table.setRowCount(0); return
        self.table.setRowCount(len(users))
        for r, data in enumerate(users):
            uid = data[0]
            for c, value in enumerate(data): self.table.setItem(r, c, QTableWidgetItem(str(value)))
            self.setup_buttons(r, uid)

    def setup_buttons(self, row, uid):
        edit_btn = QPushButton("Editar"); edit_btn.setObjectName("editButton"); edit_btn.clicked.connect(partial(self.open_edit_dialog, uid))
        del_btn = QPushButton("Eliminar"); del_btn.setObjectName("deleteButton"); del_btn.clicked.connect(partial(self.handle_delete, uid))
        self.table.setCellWidget(row, 4, edit_btn); self.table.setCellWidget(row, 5, del_btn)

    def open_add_dialog(self): UserFormDialog(on_success=self.refresh_data, parent=self).exec()

    def open_edit_dialog(self, uid):
        data, error = get_user_by_id(uid)
        if error or not data: QMessageBox.critical(self, "Error", f"No se cargaron datos del usuario: {error}"); return
        UserFormDialog(user_id=uid, user_data=data, on_success=self.refresh_data, parent=self).exec()

    def handle_delete(self, uid):
        if QMessageBox.question(self, "Confirmar", "¿Eliminar usuario?") == QMessageBox.StandardButton.Yes:
            success, msg = delete_user(uid)
            (QMessageBox.information if success else QMessageBox.critical)(self, "Resultado", msg)
            if success: self.refresh_data()

    def update_theme(self, is_dark): pass