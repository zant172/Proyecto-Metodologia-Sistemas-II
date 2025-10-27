from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..products import search_products
from ..sales_logic import process_sale

class POSWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.cart = {} 
        self.search_results = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QVBoxLayout()
        title = QLabel("Punto de Venta")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Procesa las ventas de manera rápida y eficiente")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20) # Espacio entre paneles
        
        search_panel = self.create_search_panel()
        main_layout.addWidget(search_panel, 2) # Más espacio para búsqueda
        
        cart_panel = self.create_cart_panel()
        main_layout.addWidget(cart_panel, 1) # Menos espacio para carrito
        
        layout.addLayout(main_layout)
    
    def create_search_panel(self):
        panel = QFrame()
        # Damos estilo de tarjeta al panel de búsqueda también
        panel.setObjectName("metricCard") 
        layout = QVBoxLayout(panel)
        
        search_title = QLabel("Buscar Producto")
        search_title.setObjectName("metricTitle")
        layout.addWidget(search_title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por Código o Nombre...")
        layout.addWidget(self.search_input)

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_input.textChanged.connect(lambda: self.search_timer.start(300))

        # ScrollArea para los resultados
        self.search_scroll = QScrollArea()
        self.search_scroll.setWidgetResizable(True)
        # Hacemos el fondo transparente para que tome el del panel
        self.search_scroll.setStyleSheet("background: transparent; border: none;") 
        self.search_widget = QWidget()
        self.search_widget.setStyleSheet("background: transparent;") # Ídem
        self.search_layout = QVBoxLayout(self.search_widget)
        self.search_scroll.setWidget(self.search_widget)
        
        layout.addWidget(self.search_scroll)
        
        self.refresh_search_results() # Muestra mensaje inicial
        return panel
    
    def perform_search(self):
        term = self.search_input.text()
        if len(term) < 2:
            self.search_results = []
            self.refresh_search_results()
            return
            
        products, error = search_products(term)
        if error:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Error al buscar: {error}")
            msg_box.exec()
            return

        self.search_results = products if products else []
        self.refresh_search_results()

    def refresh_search_results(self):
        # Limpia resultados anteriores
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.search_results and len(self.search_input.text()) < 2:
             empty_label = QLabel("Escriba 2 o más caracteres para buscar...")
             empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
             self.search_layout.addWidget(empty_label)
        elif not self.search_results:
             empty_label = QLabel("No se encontraron productos.")
             empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
             self.search_layout.addWidget(empty_label)

        # Muestra los nuevos resultados
        for product in self.search_results:
            product_frame = QFrame()
            # Estilo sutil para cada resultado
            product_frame.setStyleSheet("""
                QFrame { 
                    border-bottom: 1px solid rgba(100, 116, 139, 0.2); 
                    padding: 10px 0; 
                } 
                QFrame:hover { 
                    background: rgba(99, 102, 241, 0.1); 
                    border-radius: 8px;
                }
            """)
            product_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            
            product_layout = QHBoxLayout(product_frame)
            
            info_layout = QVBoxLayout()
            name_label = QLabel(product.NombreProducto)
            name_label.setStyleSheet("font-weight: bold;")
            code_label = QLabel(f"{product.Codigo} - Stock: {product.Stock}")
            code_label.setStyleSheet("font-size: 12px; color: #94A3B8;")
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(code_label)
            
            price_label = QLabel(f"${product.Precio:.2f}")
            price_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
            product_layout.addLayout(info_layout, 1)
            product_layout.addWidget(price_label)
            
            # Conecta el clic a add_to_cart
            product_frame.mousePressEvent = lambda event, p=product: self.add_to_cart(p)
            
            self.search_layout.addWidget(product_frame)
        
        self.search_layout.addStretch() # Empuja resultados hacia arriba

    def create_cart_panel(self):
        panel = QFrame()
        panel.setObjectName("cartWidget") # ID para el QSS
        layout = QVBoxLayout(panel)
        
        title = QLabel("Carrito de Venta")
        # Usamos un estilo un poco más pequeño que pageTitle
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9; margin-bottom: 15px;") 
        layout.addWidget(title)
        
        self.cart_scroll = QScrollArea()
        self.cart_scroll.setWidgetResizable(True)
        self.cart_scroll.setStyleSheet("background: transparent; border: none;")
        self.cart_widget = QWidget()
        self.cart_widget.setStyleSheet("background: transparent;")
        self.cart_layout = QVBoxLayout(self.cart_widget)
        self.cart_layout.setContentsMargins(0,0,0,0) # Sin márgenes internos
        self.cart_scroll.setWidget(self.cart_widget)
        
        layout.addWidget(self.cart_scroll)
        
        # Separador visual antes del total
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("border-top: 1px solid rgba(100, 116, 139, 0.3); margin: 15px 0;")
        layout.addWidget(separator)

        # Sección de Total
        totals_layout = QHBoxLayout()
        total_label = QLabel("TOTAL:")
        total_label.setObjectName("totalLabel") # ID para QSS
        self.total_value_label = QLabel("$0.00")
        self.total_value_label.setObjectName("totalValue") # ID para QSS
        totals_layout.addWidget(total_label)
        totals_layout.addStretch()
        totals_layout.addWidget(self.total_value_label)
        layout.addLayout(totals_layout)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 15, 0, 0) # Espacio arriba
        
        self.finalize_btn = QPushButton("Finalizar Venta")
        self.finalize_btn.setObjectName("finalizeButton") # ID para QSS
        self.finalize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.finalize_btn.clicked.connect(self.handle_finalize_sale)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setObjectName("cancelButton") # ID para QSS
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.clear_all)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.finalize_btn)
        
        layout.addLayout(buttons_layout)
        
        self.update_cart_display() # Muestra "Carrito vacío" inicialmente
        return panel
    
    def add_to_cart(self, product):
        product_id = product.idProducto
        
        if product_id in self.cart:
            item = self.cart[product_id]
            if item['cantidad'] < product.Stock:
                item['cantidad'] += 1
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Stock Insuficiente")
                msg.setText(f"No hay más stock disponible para {product.NombreProducto}.")
                msg.exec()
        else:
            if product.Stock > 0:
                self.cart[product_id] = {
                    'id': product_id,
                    'nombre': product.NombreProducto,
                    'precio': float(product.Precio), # Aseguramos que sea float
                    'cantidad': 1,
                    'stock_max': product.Stock
                }
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Sin Stock")
                msg.setText(f"El producto {product.NombreProducto} está agotado.")
                msg.exec()
        
        self.update_cart_display()
    
    def update_cart_display(self):
        # Limpia carrito anterior
        while self.cart_layout.count():
             item = self.cart_layout.takeAt(0)
             widget = item.widget()
             if widget:
                 widget.deleteLater()

        if not self.cart:
            empty_label = QLabel("Carrito vacío")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_layout.addWidget(empty_label)
        else:
            # Añade items actuales
            for product_id, item in self.cart.items():
                item_frame = QFrame()
                # Estilo sutil para cada item del carrito
                item_frame.setStyleSheet("border-bottom: 1px solid rgba(100, 116, 139, 0.2); padding: 8px 0;") 
                
                item_layout = QHBoxLayout(item_frame)
                
                info_layout = QVBoxLayout()
                name_label = QLabel(item['nombre'])
                name_label.setStyleSheet("font-weight: bold;")
                price_unit_label = QLabel(f"${item['precio']:.2f} c/u")
                price_unit_label.setStyleSheet("font-size: 12px; color: #94A3B8;")
                
                info_layout.addWidget(name_label)
                info_layout.addWidget(price_unit_label)
                
                # SpinBox para cantidad
                qty_spinbox = QSpinBox()
                qty_spinbox.setRange(1, item['stock_max'])
                qty_spinbox.setValue(item['cantidad'])
                qty_spinbox.setFixedWidth(70) # Un poco más ancho
                # Conectamos el cambio de valor a nuestra función
                qty_spinbox.valueChanged.connect(lambda value, pid=product_id: self.update_cart_quantity(pid, value))

                # Precio total y botón eliminar
                price_layout = QVBoxLayout()
                item['subtotal'] = item['precio'] * item['cantidad']
                total_price = QLabel(f"${item['subtotal']:.2f}")
                total_price.setStyleSheet("font-weight: bold;")
                total_price.setAlignment(Qt.AlignmentFlag.AlignRight)
                
                remove_btn = QPushButton("Eliminar")
                # Usamos el color rojo del QSS para el texto
                remove_btn.setStyleSheet("color: #F87171; font-size: 11px; border: none; background: transparent; padding: 0;") 
                remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                # Pasamos el item completo a remove_from_cart
                remove_btn.clicked.connect(lambda checked, i=item: self.remove_from_cart(i))
                
                price_layout.addWidget(total_price)
                price_layout.addWidget(remove_btn, 0, Qt.AlignmentFlag.AlignRight)
                
                # Ensamblamos el layout del item
                item_layout.addLayout(info_layout, 1) # Nombre y precio unitario
                item_layout.addWidget(qty_spinbox)    # Selector de cantidad
                item_layout.addLayout(price_layout)   # Precio total y eliminar
                
                self.cart_layout.addWidget(item_frame)
        
        self.cart_layout.addStretch() # Empuja items hacia arriba
        self.update_totals() # Recalcula el total general

    def update_cart_quantity(self, product_id, new_quantity):
        # Actualiza la cantidad en nuestro diccionario de carrito
        if product_id in self.cart:
             self.cart[product_id]['cantidad'] = new_quantity
             # Vuelve a dibujar el carrito con la nueva cantidad y subtotal
             self.update_cart_display()
    
    def remove_from_cart(self, item):
        # Elimina el item del diccionario usando su ID
        if item['id'] in self.cart:
            del self.cart[item['id']]
        # Vuelve a dibujar el carrito sin el item eliminado
        self.update_cart_display()
    
    def update_totals(self):
        # Calcula el total sumando los subtotales de cada item
        total = sum(item['subtotal'] for item in self.cart.values())
        self.total_value_label.setText(f"${total:.2f}")
    
    def handle_finalize_sale(self):
        if not self.cart:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Carrito Vacío")
            msg.setText("No hay productos en el carrito para vender.")
            msg.exec()
            return

        confirm = QMessageBox.question(self, "Confirmar Venta",
                                       f"Total a pagar: {self.total_value_label.text()}\n¿Desea continuar?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.No:
            return
            
        # Preparamos la lista para la lógica de venta
        cart_list = list(self.cart.values())
        success, message = process_sale(cart_list, self.user_id)
        
        msg = QMessageBox(self)
        if success:
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Venta Exitosa")
            msg.setText(message)
            msg.exec()
            self.clear_all() # Limpia el carrito y la búsqueda
        else:
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error en Venta")
            msg.setText(message)
            msg.exec()

    def clear_all(self):
        # Limpia el diccionario del carrito
        self.cart = {}
        # Vuelve a dibujar el carrito (mostrará "Carrito vacío")
        self.update_cart_display()
        # Limpia la búsqueda
        self.search_input.clear()
        self.search_results = []
        self.refresh_search_results()
    
    def refresh_data(self):
        # Al cambiar a la pestaña POS, siempre limpiamos todo
        self.clear_all()