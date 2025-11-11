from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QDoubleSpinBox, QSpinBox, 
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from ..products import get_all_categories, create_product, update_product

class ProductFormDialog(QDialog):
    def __init__(self, product_data=None, on_success=None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.on_success = on_success
        self.categories_map = {}
        
        self.product_id = self.product_data.idProducto if self.product_data else None

        self.setWindowTitle(f"{'Editar' if self.product_id else 'Agregar'} Producto")
        self.setMinimumWidth(450) # Un poco más ancho

        main_layout = QVBoxLayout(self)
        # Añadimos un margen general al diálogo
        main_layout.setContentsMargins(20, 20, 20, 20) 

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15) # Espacio vertical entre filas
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight) # Alinea labels a la derecha

        self.codigo_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.categoria_combo = QComboBox()
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0.01, 999999.99)
        self.precio_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.precio_input.setPrefix("$ ") # Prefijo de moneda
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)
        self.stock_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        form_layout.addRow("Código:", self.codigo_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Categoría:", self.categoria_combo)
        form_layout.addRow("Precio:", self.precio_input)
        form_layout.addRow("Stock:", self.stock_input)

        main_layout.addLayout(form_layout)
        # Añadimos espacio antes de los botones
        main_layout.addSpacing(20) 

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button = QPushButton("Cancelar")
        # Usamos el objectName para el estilo del botón cancelar del QSS
        self.cancel_button.setObjectName("cancelButton") 
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        buttons_layout.addStretch() # Empuja botones a la derecha
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        self.load_categories()
        if self.product_id:
            self.populate_form()

        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def load_categories(self):
        # Carga las categorías desde la base de datos
        categories, error = get_all_categories()
        if error:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudieron cargar las categorías: {error}")
            msg.exec()
            return
        
        self.categoria_combo.addItem("Seleccionar categoría...", userData=None) # Opción por defecto
        for cat_id, cat_name in categories:
            self.categories_map[cat_name] = cat_id
            self.categoria_combo.addItem(cat_name, userData=cat_id)

    def populate_form(self):
        # Rellena el formulario si estamos editando
        self.codigo_input.setText(self.product_data.Codigo)
        self.nombre_input.setText(self.product_data.NombreProducto)
        self.precio_input.setValue(self.product_data.Precio)
        self.stock_input.setValue(self.product_data.Stock)
        
        # Selecciona la categoría correcta en el ComboBox
        cat_id_to_find = self.product_data.idCategoria
        index = self.categoria_combo.findData(cat_id_to_find, role=Qt.ItemDataRole.UserDataRole)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)

    def handle_save(self):
        # Obtiene los datos del formulario
        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        precio = self.precio_input.value()
        stock = self.stock_input.value()
        cat_id = self.categoria_combo.currentData() # Obtenemos el ID guardado

        # Validaciones mejoradas
        if not codigo or not nombre or not cat_id or precio <= 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Datos incompletos")
            msg.setText("Por favor, complete todos los campos requeridos.")
            msg.exec()
            return
        
        # Validar longitud de campos
        if len(codigo) > 50:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Código muy largo")
            msg.setText("El código no puede exceder 50 caracteres.")
            msg.exec()
            return
            
        if len(nombre) > 200:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Nombre muy largo")
            msg.setText("El nombre no puede exceder 200 caracteres.")
            msg.exec()
            return
        
        # Validar caracteres especiales peligrosos
        if any(char in codigo + nombre for char in ["'", '"', ";", "--", "/*", "*/"]):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Caracteres inválidos")
            msg.setText("El código y nombre no pueden contener comillas, puntos y coma o caracteres SQL.")
            msg.exec()
            return

        try:
            # Llama a la función de lógica para crear o actualizar
            if self.product_id:
                success, message = update_product(self.product_id, codigo, nombre, cat_id, precio, stock)
            else:
                success, message = create_product(codigo, nombre, cat_id, precio, stock)
            
            # Muestra mensaje y cierra si fue exitoso
            msg = QMessageBox(self)
            if success:
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Éxito")
                msg.setText("Producto guardado correctamente.")
                msg.exec()
                if self.on_success: # Llama a la función refresh_data de la página padre
                    self.on_success()
                self.accept() # Cierra el diálogo
            else:
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error al guardar")
                msg.setText(message)
                msg.exec()
        
        except Exception as e:
            # Captura errores inesperados
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Ocurrió un error inesperado: {e}")
            msg.exec()