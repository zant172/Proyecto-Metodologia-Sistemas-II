from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QDoubleSpinBox, QSpinBox, 
                             QPushButton, QMessageBox, QHBoxLayout)
from ..products import get_all_categories, create_product, update_product # <--- CORRECCIÓN AQUÍ

class ProductFormDialog(QDialog):
    def __init__(self, product_id=None, on_success=None, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.on_success = on_success # Esta es la función para refrescar la tabla
        self.categories_map = {} # Para mapear Nombre -> idCategoria

        self.setWindowTitle(f"{'Editar' if product_id else 'Agregar'} Producto")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Campos del Formulario ---
        self.codigo_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.categoria_combo = QComboBox()
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0.01, 999999.99)
        self.precio_input.setPrefix("$ ")
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)

        form_layout.addRow("Código:", self.codigo_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Categoría:", self.categoria_combo)
        form_layout.addRow("Precio:", self.precio_input)
        form_layout.addRow("Stock:", self.stock_input)

        main_layout.addLayout(form_layout)

        # --- Botones ---
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.cancel_button = QPushButton("Cancelar")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        # --- Cargar datos ---
        self.load_categories()
        if self.product_id:
            # Lógica para cargar datos del producto si estamos editando
            # (Lo implementaremos después, por ahora nos centramos en "Crear")
            pass

        # --- Conexiones ---
        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject) # Cierra el diálogo

    def load_categories(self):
        categories, error = get_all_categories()
        if error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las categorías: {error}")
            return
        
        for cat_id, cat_name in categories:
            self.categories_map[cat_name] = cat_id
            self.categoria_combo.addItem(cat_name)

    def handle_save(self):
        # Recolectar datos del formulario
        codigo = self.codigo_input.text()
        nombre = self.nombre_input.text()
        precio = self.precio_input.value()
        stock = self.stock_input.value()
        
        # Obtener idCategoria desde el QComboBox
        cat_nombre = self.categoria_combo.currentText()
        cat_id = self.categories_map.get(cat_nombre)

        if not all([codigo, nombre, cat_id, precio > 0]):
            QMessageBox.warning(self, "Datos incompletos", "Por favor, complete todos los campos.")
            return

        # Lógica para guardar (Crear o Actualizar)
        try:
            if self.product_id:
                # Lógica de Actualización
                # success, message = update_product(self.product_id, codigo, nombre, cat_id, precio, stock)
                pass # Por ahora
            else:
                # Lógica de Creación
                success, message = create_product(codigo, nombre, cat_id, precio, stock)
            
            if success:
                QMessageBox.information(self, "Éxito", "Producto guardado correctamente.")
                if self.on_success:
                    self.on_success() # Llama a la función para refrescar la tabla
                self.accept() # Cierra el diálogo
            else:
                QMessageBox.critical(self, "Error al guardar", message)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {e}")