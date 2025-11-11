from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from functools import partial
from ..dashboard_logic import get_metodos_pago_crud, get_metodo_pago_by_id
from .metodo_pago_form_dialog import MetodoPagoFormDialog

class MetodosPagoTableWidget(QTableWidget):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.setup_table()

    def setup_table(self):
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['ID', 'Nombre', 'Tipo', 'Estado', 'Acciones'])
        header = self.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch); header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setColumnHidden(0, True); self.verticalHeader().setVisible(False); self.setShowGrid(False)

    def load_data(self):
        metodos, error = get_metodos_pago_crud()
        if error:
            msg_box = QMessageBox(self.parent_widget); msg_box.setIcon(QMessageBox.Icon.Critical); msg_box.setWindowTitle("Error DB")
            msg_box.setText(f"No se cargaron métodos de pago:\n{error}"); msg_box.exec(); self.setRowCount(0); return
        
        self.setRowCount(len(metodos))
        for row, metodo in enumerate(metodos):
            metodo_id = metodo[0]
            self.setItem(row, 0, QTableWidgetItem(str(metodo_id)))
            self.setItem(row, 1, QTableWidgetItem(metodo[1]))
            self.setItem(row, 2, QTableWidgetItem(metodo[2]))
            
            activo_text = "Activo" if metodo[3] else "Inactivo"
            estado_item = QTableWidgetItem(activo_text)
            estado_item.setForeground(QColor("#10B981") if metodo[3] else QColor("#F87171"))
            self.setItem(row, 3, estado_item)
            
            actions_widget = QWidget(); actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0); actions_layout.setSpacing(10)
            edit_btn = QPushButton("Editar"); edit_btn.setObjectName("editButton"); edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(partial(self.parent_widget.open_edit_dialog, metodo_id))
            actions_layout.addStretch(); actions_layout.addWidget(edit_btn); actions_layout.addStretch()
            self.setCellWidget(row, 4, actions_widget)

class MetodosPagoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header_layout = QVBoxLayout()
        title = QLabel("Gestión de Métodos de Pago"); title.setObjectName("pageTitle")
        subtitle = QLabel("Define las formas de pago que acepta tu negocio.")
        header_layout.addWidget(title); header_layout.addWidget(subtitle); layout.addLayout(header_layout)
        
        controls_layout = QHBoxLayout(); controls_layout.setContentsMargins(0, 10, 0, 20)
        controls_layout.addStretch()
        add_btn = QPushButton("➕ Agregar Método de Pago"); add_btn.setObjectName("addButton")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor); add_btn.clicked.connect(self.open_add_dialog)
        controls_layout.addWidget(add_btn); layout.addLayout(controls_layout)
        
        self.table = MetodosPagoTableWidget(self); layout.addWidget(self.table)

    def refresh_data(self):
        self.table.load_data()

    def open_add_dialog(self):
        dialog = MetodoPagoFormDialog(on_success=self.refresh_data, parent=self)
        dialog.exec()
        
    def open_edit_dialog(self, metodo_id):
        data, error = get_metodo_pago_by_id(metodo_id)
        if error or not data:
            msg = QMessageBox(self); msg.setIcon(QMessageBox.Icon.Critical); msg.setWindowTitle("Error")
            msg.setText(f"No se cargaron datos: {error}"); msg.exec(); return
        
        dialog = MetodoPagoFormDialog(metodo_id=metodo_id, metodo_data=data, on_success=self.refresh_data, parent=self)
        dialog.exec()