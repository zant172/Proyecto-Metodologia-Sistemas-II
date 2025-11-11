from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..products import search_products
from ..sales_logic import process_sale
from ..dashboard_logic import get_metodos_pago_activos

class POSWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.cart = {} 
        self.search_results = []
        self.metodos_pago_map = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        header_layout = QVBoxLayout()
        title = QLabel("Punto de Venta"); title.setObjectName("pageTitle")
        subtitle = QLabel("Procesa ventas rápida y eficientemente")
        header_layout.addWidget(title); header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        main_layout = QHBoxLayout(); main_layout.setSpacing(20)
        search_panel = self.create_search_panel()
        main_layout.addWidget(search_panel, 2)
        cart_panel = self.create_cart_panel()
        main_layout.addWidget(cart_panel, 1)
        layout.addLayout(main_layout)
    
    def create_search_panel(self):
        panel = QFrame(); panel.setObjectName("metricCard"); layout = QVBoxLayout(panel)
        search_title = QLabel("Buscar Producto"); search_title.setObjectName("metricTitle")
        layout.addWidget(search_title)
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Buscar por Código o Nombre...")
        layout.addWidget(self.search_input)
        self.search_timer = QTimer(self); self.search_timer.setSingleShot(True); self.search_timer.timeout.connect(self.perform_search)
        self.search_input.textChanged.connect(lambda: self.search_timer.start(300))
        self.search_scroll = QScrollArea(); self.search_scroll.setWidgetResizable(True); self.search_scroll.setStyleSheet("background: transparent; border: none;")
        self.search_widget = QWidget(); self.search_widget.setStyleSheet("background: transparent;")
        self.search_layout = QVBoxLayout(self.search_widget); self.search_scroll.setWidget(self.search_widget)
        layout.addWidget(self.search_scroll)
        self.refresh_search_results(); return panel
    
    def perform_search(self):
        term = self.search_input.text()
        if len(term) < 2: self.search_results = []; self.refresh_search_results(); return
        products, error = search_products(term)
        if error: msg = QMessageBox(self); msg.setIcon(QMessageBox.Icon.Warning); msg.setWindowTitle("Error"); msg.setText(f"Error buscar: {error}"); msg.exec(); return
        self.search_results = products if products else []; self.refresh_search_results()

    def refresh_search_results(self):
        # Limpia los widgets anteriores del layout de búsqueda
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Muestra mensaje si no hay suficientes caracteres
        if not self.search_results and len(self.search_input.text()) < 2:
            lbl = QLabel("Escriba 2+ caracteres...")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.search_layout.addWidget(lbl)
        # Muestra mensaje si no se encontraron productos
        elif not self.search_results:
            lbl = QLabel("No se encontraron productos.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.search_layout.addWidget(lbl)
        
        # Crea un widget para cada producto encontrado
        for product in self.search_results:
            p_frame = QFrame(); p_frame.setStyleSheet("QFrame { border-bottom: 1px solid rgba(100, 116, 139, 0.2); padding: 10px 0; } QFrame:hover { background: rgba(99, 102, 241, 0.1); border-radius: 8px;}"); p_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            p_layout = QHBoxLayout(p_frame)
            info = QVBoxLayout(); name = QLabel(product.NombreProducto); name.setStyleSheet("font-weight: bold;"); code = QLabel(f"{product.Codigo} - Stock: {product.Stock}"); code.setStyleSheet("font-size: 12px; color: #94A3B8;"); info.addWidget(name); info.addWidget(code)
            price = QLabel(f"${product.Precio:.2f}"); price.setStyleSheet("font-weight: bold; font-size: 14px;")
            p_layout.addLayout(info, 1); p_layout.addWidget(price)
            p_frame.mousePressEvent = lambda event, p=product: self.add_to_cart(p)
            self.search_layout.addWidget(p_frame)
        self.search_layout.addStretch()

    def create_cart_panel(self):
        panel = QFrame(); panel.setObjectName("cartWidget"); layout = QVBoxLayout(panel)
        title = QLabel("Carrito de Venta"); title.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9; margin-bottom: 15px;"); layout.addWidget(title)
        self.cart_scroll = QScrollArea(); self.cart_scroll.setWidgetResizable(True); self.cart_scroll.setStyleSheet("background: transparent; border: none;")
        self.cart_widget = QWidget(); self.cart_widget.setStyleSheet("background: transparent;")
        self.cart_layout = QVBoxLayout(self.cart_widget); self.cart_layout.setContentsMargins(0,0,0,0); self.cart_scroll.setWidget(self.cart_widget)
        layout.addWidget(self.cart_scroll)
        
        metodo_pago_layout = QFormLayout(); metodo_pago_layout.setContentsMargins(0, 10, 0, 10)
        self.metodo_pago_combo = QComboBox()
        metodo_pago_layout.addRow(QLabel("Método de Pago:"), self.metodo_pago_combo)
        layout.addLayout(metodo_pago_layout)

        separator = QFrame(); separator.setFrameShape(QFrame.Shape.HLine); separator.setStyleSheet("border-top: 1px solid rgba(100, 116, 139, 0.3); margin: 15px 0;"); layout.addWidget(separator)
        totals_layout = QHBoxLayout(); total_label = QLabel("TOTAL:"); total_label.setObjectName("totalLabel"); self.total_value_label = QLabel("$0.00"); self.total_value_label.setObjectName("totalValue"); totals_layout.addWidget(total_label); totals_layout.addStretch(); totals_layout.addWidget(self.total_value_label); layout.addLayout(totals_layout)
        buttons_layout = QHBoxLayout(); buttons_layout.setContentsMargins(0, 15, 0, 0)
        self.finalize_btn = QPushButton("Finalizar Venta"); self.finalize_btn.setObjectName("finalizeButton"); self.finalize_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.finalize_btn.clicked.connect(self.handle_finalize_sale)
        self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setObjectName("cancelButton"); self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.cancel_btn.clicked.connect(self.clear_all)
        buttons_layout.addWidget(self.cancel_btn); buttons_layout.addWidget(self.finalize_btn)
        layout.addLayout(buttons_layout)
        self.update_cart_display(); return panel
    
    def showEvent(self, event):
        """Se llama automáticamente cuando la página se muestra"""
        super().showEvent(event)
        self.load_metodos_pago()
    
    def load_metodos_pago(self):
        self.metodo_pago_combo.clear()
        self.metodos_pago_map.clear()
        metodos, error = get_metodos_pago_activos()
        if error or not metodos:
             self.metodo_pago_combo.addItem("Error al cargar", userData=None)
             return
        self.metodo_pago_combo.addItem("Seleccionar...", userData=None)
        for (id_metodo, nombre) in metodos:
            self.metodo_pago_combo.addItem(nombre, userData=id_metodo)
            self.metodos_pago_map[id_metodo] = nombre

    def add_to_cart(self, product):
        pid = product.idProducto
        if pid in self.cart:
            item = self.cart[pid]
            if item['cantidad'] < product.Stock: item['cantidad'] += 1
            else: msg = QMessageBox(self); msg.setIcon(QMessageBox.Icon.Warning); msg.setWindowTitle("Stock Insuf."); msg.setText(f"No hay más stock para {product.NombreProducto}."); msg.exec()
        else:
            if product.Stock > 0: self.cart[pid] = {'id': pid, 'nombre': product.NombreProducto, 'precio': float(product.Precio), 'cantidad': 1, 'stock_max': product.Stock}
            else: msg = QMessageBox(self); msg.setIcon(QMessageBox.Icon.Warning); msg.setWindowTitle("Sin Stock"); msg.setText(f"{product.NombreProducto} agotado."); msg.exec()
        self.update_cart_display()
    
    def update_cart_display(self):
        # Limpia los widgets anteriores del carrito
        while self.cart_layout.count():
            item = self.cart_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Muestra mensaje si el carrito está vacío
        if not self.cart:
            lbl = QLabel("Carrito vacío")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_layout.addWidget(lbl)
        else:
            for pid, item in self.cart.items():
                i_frame = QFrame(); i_frame.setStyleSheet("border-bottom: 1px solid rgba(100, 116, 139, 0.2); padding: 8px 0;")
                i_layout = QHBoxLayout(i_frame)
                info = QVBoxLayout(); name = QLabel(item['nombre']); name.setStyleSheet("font-weight: bold;"); price_u = QLabel(f"${item['precio']:.2f} c/u"); price_u.setStyleSheet("font-size: 12px; color: #94A3B8;"); info.addWidget(name); info.addWidget(price_u)
                qty = QSpinBox(); qty.setRange(1, item['stock_max']); qty.setValue(item['cantidad']); qty.setFixedWidth(70); qty.valueChanged.connect(lambda val, p=pid: self.update_cart_quantity(p, val))
                price_l = QVBoxLayout(); item['subtotal'] = item['precio'] * item['cantidad']; total_p = QLabel(f"${item['subtotal']:.2f}"); total_p.setStyleSheet("font-weight: bold;"); total_p.setAlignment(Qt.AlignmentFlag.AlignRight)
                remove = QPushButton("Eliminar"); remove.setStyleSheet("color: #F87171; font-size: 11px; border: none; background: transparent; padding: 0;"); remove.setCursor(Qt.CursorShape.PointingHandCursor); remove.clicked.connect(lambda chk, i=item: self.remove_from_cart(i)); price_l.addWidget(total_p); price_l.addWidget(remove, 0, Qt.AlignmentFlag.AlignRight)
                i_layout.addLayout(info, 1); i_layout.addWidget(qty); i_layout.addLayout(price_l)
                self.cart_layout.addWidget(i_frame)
        self.cart_layout.addStretch(); self.update_totals()

    def update_cart_quantity(self, pid, qty):
        if pid in self.cart: self.cart[pid]['cantidad'] = qty; self.update_cart_display()

    def remove_from_cart(self, item):
        if item['id'] in self.cart: del self.cart[item['id']]; self.update_cart_display()

    def update_totals(self):
        total = sum(item['subtotal'] for item in self.cart.values())
        self.total_value_label.setText(f"${total:.2f}")

    def handle_finalize_sale(self):
        if not self.cart: msg = QMessageBox(self); msg.setIcon(QMessageBox.Icon.Warning); msg.setWindowTitle("Vacío"); msg.setText("Carrito vacío."); msg.exec(); return
        
        id_metodo_pago = self.metodo_pago_combo.currentData()
        if not id_metodo_pago:
            msg = QMessageBox(self); msg.setIcon(QMessageBox.Icon.Warning); msg.setWindowTitle("Inválido"); msg.setText("Selecciona un método de pago."); msg.exec(); return
            
        confirm = QMessageBox.question(self, "Confirmar Venta", f"Total: {self.total_value_label.text()}\nMétodo: {self.metodo_pago_combo.currentText()}\n¿Continuar?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No: return

        cart_list = []
        for pid, item in self.cart.items():
             cart_list.append({'id': item['id'], 'cantidad': item['cantidad'], 'precio': item['precio'], 'subtotal': item['subtotal'], 'nombre': item['nombre']})

        success, message = process_sale(cart_list, self.user_id, id_metodo_pago)
        msg = QMessageBox(self)
        if success: msg.setIcon(QMessageBox.Icon.Information); msg.setWindowTitle("Éxito"); msg.setText(message); msg.exec(); self.clear_all()
        else: msg.setIcon(QMessageBox.Icon.Critical); msg.setWindowTitle("Error"); msg.setText(message); msg.exec()

    def clear_all(self):
        self.cart = {}; self.update_cart_display(); self.search_input.clear(); self.search_results = []; self.refresh_search_results(); self.load_metodos_pago()
    
    def refresh_data(self):
        self.clear_all()