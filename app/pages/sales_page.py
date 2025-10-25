from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView, QLineEdit, QSpinBox
from PyQt6.QtCore import Qt, QTimer
from ..products import search_products
from ..sales_logic import process_sale

class SalesPage(QWidget):
    def __init__(self, user_id):
        super().__init__(); self.user_id = user_id; self.cart = {}
        main_layout = QHBoxLayout(self); left_panel = QWidget(); left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 2)
        right_panel = QWidget(); right_panel.setObjectName("cartWidget"); right_panel.setFixedWidth(400)
        right_layout = QVBoxLayout(right_panel); main_layout.addWidget(right_panel)
        title = QLabel("Punto de Venta (POS)"); title.setObjectName("pageTitle"); left_layout.addWidget(title)
        self.search_input = QLineEdit(placeholderText="Buscar..."); left_layout.addWidget(self.search_input)
        self.search_table = QTableWidget(); self.search_table.setColumnCount(5); self.search_table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Precio", "Stock"])
        self.search_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.search_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.search_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection); header = self.search_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch); header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.search_table.setColumnHidden(0, True); left_layout.addWidget(self.search_table)
        self.search_timer = QTimer(self); self.search_timer.setSingleShot(True); self.search_timer.timeout.connect(self.perform_search)
        self.search_input.textChanged.connect(lambda: self.search_timer.start(300)); self.search_table.doubleClicked.connect(self.add_from_search)
        cart_title = QLabel("Carrito"); cart_title.setObjectName("pageTitle"); right_layout.addWidget(cart_title)
        self.cart_table = QTableWidget(); self.cart_table.setColumnCount(5); self.cart_table.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Cant.", "Subtotal"])
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); header_cart = self.cart_table.horizontalHeader()
        header_cart.setSectionResizeMode(QHeaderView.ResizeMode.Stretch); header_cart.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setColumnHidden(0, True); self.cart_table.setColumnWidth(3, 70); right_layout.addWidget(self.cart_table)
        total_layout = QHBoxLayout(); total_label = QLabel("TOTAL:"); total_label.setObjectName("totalLabel")
        self.total_value = QLabel("$0.00"); self.total_value.setObjectName("totalValue"); total_layout.addWidget(total_label); total_layout.addStretch(); total_layout.addWidget(self.total_value)
        right_layout.addLayout(total_layout)
        buttons_layout = QHBoxLayout(); self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setObjectName("cancelButton")
        self.finalize_btn = QPushButton("Finalizar Venta"); self.finalize_btn.setObjectName("finalizeButton")
        buttons_layout.addWidget(self.cancel_btn); buttons_layout.addWidget(self.finalize_btn); right_layout.addLayout(buttons_layout)
        self.cancel_btn.clicked.connect(self.clear_all); self.finalize_btn.clicked.connect(self.handle_finalize)

    def perform_search(self):
        term = self.search_input.text()
        if len(term) < 2: self.search_table.setRowCount(0); return
        products, error = search_products(term)
        if error: QMessageBox.warning(self, "Error", f"Error al buscar: {error}"); return
        self.search_table.setRowCount(len(products))
        for r, p in enumerate(products):
            self.search_table.setItem(r, 0, QTableWidgetItem(str(p.idProducto))); self.search_table.setItem(r, 1, QTableWidgetItem(p.Codigo))
            self.search_table.setItem(r, 2, QTableWidgetItem(p.NombreProducto)); self.search_table.setItem(r, 3, QTableWidgetItem(f"${p.Precio:.2f}"))
            self.search_table.setItem(r, 4, QTableWidgetItem(str(p.Stock)))

    def add_from_search(self, index):
        r = index.row(); pid = int(self.search_table.item(r, 0).text()); name = self.search_table.item(r, 2).text()
        price = float(self.search_table.item(r, 3).text().replace('$', '')); stock = int(self.search_table.item(r, 4).text())
        self.add_to_cart(pid, name, price, stock)

    def add_to_cart(self, pid, name, price, stock):
        if pid in self.cart:
            if self.cart[pid]['cantidad'] < stock: self.cart[pid]['cantidad'] += 1
            else: QMessageBox.warning(self, "Stock Límite", f"No hay más stock de {name}."); return
        else: self.cart[pid] = {'id': pid, 'nombre': name, 'precio': price, 'cantidad': 1, 'stock_max': stock, 'subtotal': price}
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.blockSignals(True); self.cart_table.setRowCount(len(self.cart)); total = 0
        for r, (pid, item) in enumerate(self.cart.items()):
            item['subtotal'] = item['precio'] * item['cantidad']; total += item['subtotal']
            self.cart_table.setItem(r, 0, QTableWidgetItem(str(item['id']))); self.cart_table.setItem(r, 1, QTableWidgetItem(item['nombre']))
            self.cart_table.setItem(r, 2, QTableWidgetItem(f"${item['precio']:.2f}"))
            spin = QSpinBox(); spin.setRange(1, item['stock_max']); spin.setValue(item['cantidad']); spin.setProperty("pid", pid)
            spin.valueChanged.connect(self.update_qty)
            self.cart_table.setCellWidget(r, 3, spin); self.cart_table.setItem(r, 4, QTableWidgetItem(f"${item['subtotal']:.2f}"))
        self.total_value.setText(f"${total:.2f}"); self.cart_table.blockSignals(False)

    def update_qty(self, qty):
        sender = self.sender(); pid = sender.property("pid")
        if pid in self.cart: self.cart[pid]['cantidad'] = qty; self.refresh_cart()

    def clear_all(self): self.cart = {}; self.refresh_cart(); self.search_input.clear(); self.search_table.setRowCount(0)

    def handle_finalize(self):
        if not self.cart: QMessageBox.warning(self, "Vacío", "Carrito vacío."); return
        if QMessageBox.question(self, "Confirmar", f"Total: {self.total_value.text()}\n¿Continuar?") == QMessageBox.StandardButton.Yes:
            success, msg = process_sale(list(self.cart.values()), self.user_id)
            (QMessageBox.information if success else QMessageBox.critical)(self, "Resultado", msg)
            if success: self.clear_all()

    def refresh_data(self): self.clear_all()
    def update_theme(self, is_dark): pass