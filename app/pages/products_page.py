from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
from functools import partial
from ..products import get_all_products, get_product_by_id, delete_product
from .product_form_dialog import ProductFormDialog

class ProductsPage(QWidget):
    def __init__(self):
        super().__init__(); layout = QVBoxLayout(self); header_layout = QHBoxLayout()
        title = QLabel("Gestión de Stock"); title.setObjectName("pageTitle"); header_layout.addWidget(title); header_layout.addStretch()
        self.add_button = QPushButton("Agregar Producto"); self.add_button.setObjectName("addButton"); header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        self.table = QTableWidget(); self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Categoría", "Precio", "Stock", "Editar", "Eliminar"])
        self.table.verticalHeader().setVisible(False); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 50); self.table.setColumnWidth(6, 70); self.table.setColumnWidth(7, 70)
        layout.addWidget(self.table); self.refresh_data(); self.add_button.clicked.connect(self.open_add_dialog)

    def refresh_data(self): self.load_products()

    def load_products(self):
        products, error = get_all_products()
        if error: QMessageBox.critical(self, "Error DB", f"No se cargaron productos:\n{error}"); self.table.setRowCount(0); return
        self.table.setRowCount(len(products))
        for r, data in enumerate(products):
            pid = data[0]
            for c, value in enumerate(data):
                item = QTableWidgetItem(f"${value:.2f}" if c == 4 else str(value)); self.table.setItem(r, c, item)
            self.setup_buttons(r, pid)

    def setup_buttons(self, row, pid):
        edit_btn = QPushButton("Editar"); edit_btn.setObjectName("editButton"); edit_btn.clicked.connect(partial(self.open_edit_dialog, pid))
        del_btn = QPushButton("Eliminar"); del_btn.setObjectName("deleteButton"); del_btn.clicked.connect(partial(self.handle_delete, pid))
        self.table.setCellWidget(row, 6, edit_btn); self.table.setCellWidget(row, 7, del_btn)

    def open_add_dialog(self): ProductFormDialog(on_success=self.refresh_data, parent=self).exec()

    def open_edit_dialog(self, pid):
        data, error = get_product_by_id(pid)
        if error or not data: QMessageBox.critical(self, "Error", f"No se cargaron datos del producto: {error}"); return
        class ProductData: idProducto=pid; Codigo=data[0]; NombreProducto=data[1]; idCategoria=data[2]; Precio=data[3]; Stock=data[4]
        ProductFormDialog(product_data=ProductData, on_success=self.refresh_data, parent=self).exec()

    def handle_delete(self, pid):
        if QMessageBox.question(self, "Confirmar", "¿Eliminar producto?") == QMessageBox.StandardButton.Yes:
            success, msg = delete_product(pid)
            (QMessageBox.information if success else QMessageBox.critical)(self, "Resultado", msg)
            if success: self.refresh_data()

    def update_theme(self, is_dark): pass