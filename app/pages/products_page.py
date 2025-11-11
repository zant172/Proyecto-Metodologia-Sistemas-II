from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from functools import partial
from ..products import get_all_products, get_product_by_id, delete_product
from .product_form_dialog import ProductFormDialog

class ProductTableWidget(QTableWidget):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.setup_table()
    
    def setup_table(self):
        self.setColumnCount(7) 
        self.setHorizontalHeaderLabels(['ID', 'Código', 'Nombre Producto', 'Categoría', 'Precio Venta', 'Stock Actual', 'Acciones'])
        
        header = self.horizontalHeader()
        # Permitimos que las columnas se ajusten pero damos prioridad al nombre
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Nombre Producto
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed) # Acciones - ancho fijo
        header.resizeSection(6, 240) # Ancho mínimo para columna Acciones
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setColumnHidden(0, True) # Ocultamos ID
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False) # Quitamos líneas de grid internas si el QSS ya las maneja
    
    def load_products(self):
        products, error = get_all_products()
        if error:
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error de Base de Datos")
            msg_box.setText(f"No se pudieron cargar los productos:\n{error}")
            msg_box.exec()
            self.setRowCount(0)
            return
            
        self.setRowCount(len(products))
        
        for row, product in enumerate(products):
            product_id = product[0]
            
            # Columnas de datos
            self.setItem(row, 0, QTableWidgetItem(str(product_id)))
            self.setItem(row, 1, QTableWidgetItem(product[1])) # Codigo
            self.setItem(row, 2, QTableWidgetItem(product[2])) # Nombre
            self.setItem(row, 3, QTableWidgetItem(product[3])) # Categoria
            
            price_item = QTableWidgetItem(f"${product[4]:.2f}") # Precio
            self.setItem(row, 4, price_item)
            
            stock_item = QTableWidgetItem(str(product[5])) # Stock
            stock = product[5]
            # Usamos colores del QSS para el texto del stock
            if stock < 5:
                stock_item.setForeground(QColor('#F87171')) # Rojo suave del QSS
            elif stock < 15:
                stock_item.setForeground(QColor('#FBBF24')) # Naranja suave del QSS
            # Si no, usa el color por defecto del QSS
            self.setItem(row, 5, stock_item)
            
            # Columna de Acciones
            actions_widget = QWidget()
            actions_widget.setMinimumHeight(50) # Altura mínima para que los botones sean visibles
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4) # Márgenes para dar espacio
            actions_layout.setSpacing(8) # Espacio entre botones
            
            edit_btn = QPushButton("✎ Editar")
            edit_btn.setObjectName("editButton") # ID para el QSS
            edit_btn.setMinimumSize(90, 36) # Tamaño mínimo explícito
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(partial(self.parent_widget.open_edit_dialog, product_id))
            
            delete_btn = QPushButton("🗑 Eliminar")
            delete_btn.setObjectName("deleteButton") # ID para el QSS
            delete_btn.setMinimumSize(100, 36) # Tamaño mínimo explícito
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(partial(self.parent_widget.handle_delete, product_id))
            
            actions_layout.addStretch() # Empuja botones al centro
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch() # Centra los botones
            
            self.setCellWidget(row, 6, actions_widget)
            self.setRowHeight(row, 56) # Altura de fila para acomodar botones

class InventoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QVBoxLayout()
        title = QLabel("Gestión de Inventario")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Administra tus productos y stock")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Controles (Búsqueda y Agregar)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 20) # Espacio vertical
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar producto...")
        
        add_btn = QPushButton("➕ Agregar Producto")
        add_btn.setObjectName("addButton") # ID para el QSS
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_dialog)
        
        controls_layout.addWidget(search_input, 1) # Que la búsqueda ocupe más espacio
        controls_layout.addWidget(add_btn)
        layout.addLayout(controls_layout)
        
        # Tabla de productos
        self.products_table = ProductTableWidget(self)
        layout.addWidget(self.products_table)
        
    def refresh_data(self):
        # Este método es llamado por MainWindow al cambiar de pestaña
        self.products_table.load_products()

    def open_add_dialog(self):
        # Abre el diálogo para agregar un nuevo producto
        dialog = ProductFormDialog(on_success=self.refresh_data, parent=self)
        # El QSS de QMessageBox se aplicará automáticamente
        dialog.exec()
    
    def open_edit_dialog(self, product_id):
        # Busca los datos del producto por ID
        product_data_tuple, error = get_product_by_id(product_id)
        if error or not product_data_tuple:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"No se pudieron cargar los datos del producto: {error}")
            msg_box.exec()
            return
        
        # Empaqueta los datos para el diálogo (como antes)
        full_product_data = (product_id,) + product_data_tuple
        class ProductData:
            def __init__(self, data):
                self.idProducto = data[0]
                self.Codigo = data[1]
                self.NombreProducto = data[2]
                self.idCategoria = data[3]
                self.Precio = data[4]
                self.Stock = data[5]

        # Abre el diálogo para editar
        dialog = ProductFormDialog(product_data=ProductData(full_product_data), on_success=self.refresh_data, parent=self)
        dialog.exec()

    def handle_delete(self, product_id):
        # Muestra un diálogo de confirmación antes de eliminar
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar este producto?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Llama a la función de lógica para eliminar (soft delete)
            success, message = delete_product(product_id)
            # Muestra un mensaje de éxito o error
            msg_box = QMessageBox(self)
            if success:
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("Éxito")
            else:
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("Error")
            msg_box.setText(message)
            msg_box.exec()
            # Refresca la tabla si la eliminación fue exitosa
            if success:
                self.refresh_data()