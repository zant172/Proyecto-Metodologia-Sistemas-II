from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt
from ..products import get_all_categories, create_product, update_product

class ProductFormDialog(QDialog):
    def __init__(self, product_data=None, on_success=None, parent=None):
        super().__init__(parent); self.product_data = product_data; self.on_success = on_success; self.categories_map = {}
        self.product_id = self.product_data.idProducto if self.product_data else None
        self.setWindowTitle(f"{'Editar' if self.product_id else 'Agregar'} Producto"); self.setMinimumWidth(400)
        main_layout = QVBoxLayout(self); form_layout = QFormLayout()
        self.codigo_input = QLineEdit(); self.nombre_input = QLineEdit(); self.categoria_combo = QComboBox()
        self.precio_input = QDoubleSpinBox(); self.precio_input.setRange(0.01, 999999.99); self.precio_input.setPrefix("$ ")
        self.stock_input = QSpinBox(); self.stock_input.setRange(0, 99999)
        form_layout.addRow("Código:", self.codigo_input); form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Categoría:", self.categoria_combo); form_layout.addRow("Precio:", self.precio_input); form_layout.addRow("Stock:", self.stock_input)
        main_layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout(); self.save_button = QPushButton("Guardar"); self.cancel_button = QPushButton("Cancelar")
        buttons_layout.addStretch(); buttons_layout.addWidget(self.cancel_button); buttons_layout.addWidget(self.save_button)
        main_layout.addLayout(buttons_layout); self.load_categories()
        if self.product_id: self.populate_form()
        self.save_button.clicked.connect(self.handle_save); self.cancel_button.clicked.connect(self.reject)

    def load_categories(self):
        categories, error = get_all_categories()
        if error: QMessageBox.critical(self, "Error", f"No se cargaron categorías: {error}"); return
        for cat_id, cat_name in categories: self.categories_map[cat_name] = cat_id; self.categoria_combo.addItem(cat_name, userData=cat_id)

    def populate_form(self):
        self.codigo_input.setText(self.product_data.Codigo); self.nombre_input.setText(self.product_data.NombreProducto)
        self.precio_input.setValue(self.product_data.Precio); self.stock_input.setValue(self.product_data.Stock)
        index = self.categoria_combo.findData(self.product_data.idCategoria, role=Qt.ItemDataRole.UserDataRole)
        if index >= 0: self.categoria_combo.setCurrentIndex(index)

    def handle_save(self):
        codigo = self.codigo_input.text(); nombre = self.nombre_input.text(); precio = self.precio_input.value(); stock = self.stock_input.value()
        cat_id = self.categories_map.get(self.categoria_combo.currentText())
        if not all([codigo, nombre, cat_id, precio > 0]): QMessageBox.warning(self, "Datos incompletos", "Complete todos los campos."); return
        try:
            func = update_product if self.product_id else create_product
            args = (self.product_id, codigo, nombre, cat_id, precio, stock) if self.product_id else (codigo, nombre, cat_id, precio, stock)
            success, message = func(*args)
            if success: QMessageBox.information(self, "Éxito", message); self.on_success and self.on_success(); self.accept()
            else: QMessageBox.critical(self, "Error al guardar", message)
        except Exception as e: QMessageBox.critical(self, "Error", f"Error inesperado: {e}")