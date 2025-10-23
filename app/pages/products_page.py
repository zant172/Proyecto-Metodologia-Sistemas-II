from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QAbstractItemView)
from functools import partial
from ..products import get_all_products, get_product_by_id, delete_product # <--- CORRECCIÓN 1
from .product_form_dialog import ProductFormDialog # <--- CORRECCIÓN 2

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
        # Añadimos 2 columnas para los botones de acciones
        self.product_table.setColumnCount(8) 
        self.product_table.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Precio", "Stock", "Editar", "Eliminar"
        ])
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Ajustar el tamaño de las columnas
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Nombre
        self.product_table.setColumnWidth(0, 50)  # ID
        self.product_table.setColumnWidth(6, 70)  # Editar
        self.product_table.setColumnWidth(7, 70)  # Eliminar

        layout.addWidget(self.product_table)
        
        self.load_products()
        
        # Conectar el botón de agregar
        self.add_product_button.clicked.connect(self.open_add_dialog)

    def load_products(self):
        """Carga y recarga los datos de la tabla."""
        products, error = get_all_products()
        
        if error:
            QMessageBox.critical(self, "Error de Base de Datos", 
                                 f"No se pudieron cargar los productos:\n{error}")
            self.product_table.setRowCount(0) # Limpiar tabla en caso de error
            return
            
        self.product_table.setRowCount(len(products))
        
        for row_idx, row_data in enumerate(products):
            # row_data = (idProducto, Codigo, Nombre, Categoria, Precio, Stock)
            product_id = row_data[0]
            
            # Cargar datos en las celdas
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.product_table.setItem(row_idx, col_idx, item)
            
            # Añadir botones de "Editar" y "Eliminar"
            self.setup_table_buttons(row_idx, product_id)

    def setup_table_buttons(self, row, product_id):
        # Botón Editar
        edit_button = QPushButton("Editar")
        edit_button.setObjectName("editButton")
        # 'partial' nos permite pasar argumentos (product_id) al slot
        edit_button.clicked.connect(partial(self.open_edit_dialog, product_id))
        self.product_table.setCellWidget(row, 6, edit_button) 

        # Botón Eliminar
        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(partial(self.handle_delete, product_id))
        self.product_table.setCellWidget(row, 7, delete_button)

    def refresh_table(self):
        """Función de callback para recargar la tabla."""
        self.load_products()

    def open_add_dialog(self):
        """Abre el formulario para crear un nuevo producto."""
        dialog = ProductFormDialog(on_success=self.refresh_table, parent=self)
        dialog.exec() # Muestra el diálogo de forma modal

    def open_edit_dialog(self, product_id):
        """Abre el formulario para editar un producto existente."""
        # 1. Obtener los datos actuales del producto
        product_data, error = get_product_by_id(product_id)
        if error or not product_data:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos del producto: {error}")
            return
        
        # 2. Abrir el diálogo y "rellenar" los campos
        dialog = ProductFormDialog(product_id=product_id, on_success=self.refresh_table, parent=self)
        
        # Rellenar el formulario con los datos
        # (Codigo, NombreProducto, idCategoria, Precio, Stock)
        dialog.codigo_input.setText(product_data.Codigo)
        dialog.nombre_input.setText(product_data.NombreProducto)
        dialog.precio_input.setValue(product_data.Precio)
        dialog.stock_input.setValue(product_data.Stock)
        
        # Seleccionar la categoría correcta en el QComboBox
        # (Esta lógica aún debe afinarse)
        
        dialog.exec()

    def handle_delete(self, product_id):
        """Maneja la lógica de borrado lógico."""
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar este producto?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = delete_product(product_id)
            if success:
                QMessageBox.information(self, "Éxito", message)
                self.refresh_table()
            else:
                QMessageBox.critical(self, "Error", message)