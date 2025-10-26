from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QAbstractItemView)
from functools import partial
from ..products import get_all_products, get_product_by_id, delete_product
from .product_form_dialog import ProductFormDialog

class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel("Gestión de Stock de Productos")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_product_button = QPushButton("Agregar Producto")
        self.add_product_button.setObjectName("addButton")
        header_layout.addWidget(self.add_product_button)
        layout.addLayout(header_layout)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(8) 
        self.product_table.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Precio", "Stock", "Editar", "Eliminar"
        ])
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.product_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.product_table)
        
        self.refresh_data()
        
        self.add_product_button.clicked.connect(self.open_add_dialog)
    
    def refresh_data(self):
        self.load_products()

    def load_products(self):
        products, error = get_all_products()
        
        if error:
            QMessageBox.critical(self, "Error de Base de Datos", 
                                 f"No se pudieron cargar los productos:\n{error}")
            self.product_table.setRowCount(0)
            return
            
        self.product_table.setRowCount(len(products))
        
        for row_idx, row_data in enumerate(products):
            product_id = row_data[0]
            
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                if col_idx == 4:
                    item.setText(f"${col_data:.2f}")
                self.product_table.setItem(row_idx, col_idx, item)
            
            self.setup_table_buttons(row_idx, product_id)

    def setup_table_buttons(self, row, product_id):
        edit_button = QPushButton("Editar")
        edit_button.setObjectName("editButton")
        edit_button.clicked.connect(partial(self.open_edit_dialog, product_id))
        self.product_table.setCellWidget(row, 6, edit_button) 

        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(partial(self.handle_delete, product_id))
        self.product_table.setCellWidget(row, 7, delete_button)

    def open_add_dialog(self):
        dialog = ProductFormDialog(on_success=self.refresh_data, parent=self)
        dialog.exec()

    def open_edit_dialog(self, product_id):
        product_data, error = get_product_by_id(product_id)
        if error or not product_data:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos del producto: {error}")
            return
        
        full_product_data = (product_id,) + product_data
        
        class ProductData:
            def __init__(self, data):
                self.idProducto = data[0]
                self.Codigo = data[1]
                self.NombreProducto = data[2]
                self.idCategoria = data[3]
                self.Precio = data[4]
                self.Stock = data[5]

        dialog = ProductFormDialog(product_data=ProductData(full_product_data), on_success=self.refresh_data, parent=self)
        dialog.exec()

    def handle_delete(self, product_id):
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar este producto?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = delete_product(product_id)
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", message)