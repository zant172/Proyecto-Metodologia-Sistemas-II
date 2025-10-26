from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QAbstractItemView, QLineEdit,
                             QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer
from ..products import search_products
from ..sales_logic import process_sale

class SalesPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.cart = {} # {product_id: {datos...}}
        
        main_layout = QHBoxLayout(self)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 2)

        right_panel = QWidget()
        right_panel.setObjectName("cartWidget")
        right_panel.setFixedWidth(400)
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel)

        title = QLabel("Punto de Venta (POS)")
        title.setObjectName("pageTitle")
        left_layout.addWidget(title)

        self.search_input = QLineEdit(placeholderText="Buscar por Código o Nombre...")
        left_layout.addWidget(self.search_input)

        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(5)
        self.search_results_table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Precio", "Stock"])
        self.search_results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.search_results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.search_results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.search_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.search_results_table.setColumnHidden(0, True)
        left_layout.addWidget(self.search_results_table)

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_input.textChanged.connect(lambda: self.search_timer.start(300))
        self.search_results_table.doubleClicked.connect(self.add_to_cart_from_search)

        cart_title = QLabel("Carrito de Compra")
        cart_title.setObjectName("pageTitle")
        right_layout.addWidget(cart_title)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Cant.", "Subtotal"])
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setColumnHidden(0, True)
        self.cart_table.setColumnWidth(3, 70)
        right_layout.addWidget(self.cart_table)
        
        self.cart_table.cellChanged.connect(self.update_cart_subtotal)

        total_layout = QHBoxLayout()
        total_label = QLabel("TOTAL:")
        total_label.setObjectName("totalLabel")
        self.total_value_label = QLabel("$0.00")
        self.total_value_label.setObjectName("totalValue")
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_value_label)
        right_layout.addLayout(total_layout)

        buttons_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("cancelButton")
        self.finalize_button = QPushButton("Finalizar Venta")
        self.finalize_button.setObjectName("finalizeButton")
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.finalize_button)
        right_layout.addLayout(buttons_layout)

        self.cancel_button.clicked.connect(self.clear_all)
        self.finalize_button.clicked.connect(self.handle_finalize_sale)

    def perform_search(self):
        term = self.search_input.text()
        if len(term) < 2:
            self.search_results_table.setRowCount(0)
            return
            
        products, error = search_products(term)
        if error:
            QMessageBox.warning(self, "Error", f"Error al buscar: {error}")
            return

        self.search_results_table.setRowCount(len(products))
        for row, prod in enumerate(products):
            self.search_results_table.setItem(row, 0, QTableWidgetItem(str(prod.idProducto)))
            self.search_results_table.setItem(row, 1, QTableWidgetItem(prod.Codigo))
            self.search_results_table.setItem(row, 2, QTableWidgetItem(prod.NombreProducto))
            self.search_results_table.setItem(row, 3, QTableWidgetItem(f"${prod.Precio:.2f}"))
            self.search_results_table.setItem(row, 4, QTableWidgetItem(str(prod.Stock)))

    def add_to_cart_from_search(self, index):
        row = index.row()
        product_id = int(self.search_results_table.item(row, 0).text())
        nombre = self.search_results_table.item(row, 2).text()
        precio_str = self.search_results_table.item(row, 3).text().replace('$', '')
        precio = float(precio_str)
        stock = int(self.search_results_table.item(row, 4).text())

        self.add_product_to_cart(product_id, nombre, precio, stock)

    def add_product_to_cart(self, product_id, nombre, precio, stock):
        if product_id in self.cart:
            current_qty = self.cart[product_id]['cantidad']
            if current_qty < stock:
                self.cart[product_id]['cantidad'] += 1
            else:
                QMessageBox.warning(self, "Stock Insuficiente", f"No hay más stock disponible para {nombre}.")
        else:
            self.cart[product_id] = {
                'id': product_id,
                'nombre': nombre,
                'precio': precio,
                'cantidad': 1,
                'stock_max': stock,
                'subtotal': precio
            }
        
        self.refresh_cart_table()

    def refresh_cart_table(self):
        self.cart_table.blockSignals(True)
        self.cart_table.setRowCount(len(self.cart))
        
        total_general = 0
        
        for row, (product_id, item) in enumerate(self.cart.items()):
            
            item['subtotal'] = item['precio'] * item['cantidad']
            total_general += item['subtotal']
            
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['nombre']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"${item['precio']:.2f}"))
            
            qty_spinbox = QSpinBox()
            qty_spinbox.setRange(1, item['stock_max'])
            qty_spinbox.setValue(item['cantidad'])
            qty_spinbox.setProperty("product_id", product_id)
            qty_spinbox.valueChanged.connect(self.update_cart_quantity)
            
            self.cart_table.setCellWidget(row, 3, qty_spinbox)
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"${item['subtotal']:.2f}"))
            
        self.total_value_label.setText(f"${total_general:.2f}")
        self.cart_table.blockSignals(False)

    def update_cart_quantity(self, new_quantity):
        sender = self.sender()
        if sender:
            product_id = sender.property("product_id")
            if product_id in self.cart:
                self.cart[product_id]['cantidad'] = new_quantity
                self.refresh_cart_table()

    def update_cart_subtotal(self, row, column):
        pass

    def clear_all(self):
        self.cart = {}
        self.refresh_cart_table()
        self.search_input.clear()
        self.search_results_table.setRowCount(0)

    def handle_finalize_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "Carrito Vacío", "No hay productos en el carrito para vender.")
            return

        confirm = QMessageBox.question(self, "Confirmar Venta",
                                       f"Total a pagar: {self.total_value_label.text()}\n¿Desea continuar?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.No:
            return
            
        cart_list = list(self.cart.values())
        success, message = process_sale(cart_list, self.user_id)
        
        if success:
            QMessageBox.information(self, "Venta Exitosa", message)
            self.clear_all()
        else:
            QMessageBox.critical(self, "Error en Venta", message)