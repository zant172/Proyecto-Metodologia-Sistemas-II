from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QStackedWidget, QListWidgetItem, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton, QLabel)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from app.products import get_all_products

class MainWindow(QMainWindow):
    def __init__(self, user_role):
        super().__init__()
        self.user_role = user_role
        
        self.setWindowTitle("InfinityTech - Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_stylesheet())

        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.nav_bar = QListWidget()
        self.nav_bar.setFixedWidth(200)
        main_layout.addWidget(self.nav_bar)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.create_pages()
        
        self.nav_bar.currentItemChanged.connect(
            lambda current: self.stacked_widget.setCurrentIndex(self.nav_bar.row(current))
        )
        
        self.setup_ui_for_role()
        self.nav_bar.setCurrentRow(0)

    def create_pages(self):
        pages = {
            "Inicio": "home.svg",
            "Productos": "package.svg",
            "Punto de Venta": "shopping-cart.svg",
            "Gestión de Usuarios": "users.svg",
            "Reportes": "bar-chart-2.svg"
        }

        for name, icon_path in pages.items():
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.nav_bar.addItem(item)
            
            page = QWidget()
            page.setObjectName(f"page_{name.replace(' ', '_')}")
            self.stacked_widget.addWidget(page)
        
        self.setup_products_page()

    def setup_products_page(self):
        page = self.findChild(QWidget, "page_Productos")
        layout = QVBoxLayout(page)
        
        header_layout = QHBoxLayout()
        title = QLabel("Gestión de Stock de Productos")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_product_button = QPushButton("Agregar Producto")
        add_product_button.setObjectName("addButton")
        header_layout.addWidget(add_product_button)
        layout.addLayout(header_layout)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Categoría", "Precio", "Stock"])
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.product_table)
        
        self.load_products()

    def load_products(self):
        products = get_all_products()
        self.product_table.setRowCount(len(products))
        
        for row_idx, row_data in enumerate(products):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.product_table.setItem(row_idx, col_idx, item)

    def setup_ui_for_role(self):
        if self.user_role == 'Usuario':
            for i in range(self.nav_bar.count()):
                item = self.nav_bar.item(i)
                if item.text() in ["Gestión de Usuarios", "Reportes"]:
                    item.setHidden(True)

    def get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #2c3e50;
            }
            QListWidget {
                background-color: #34495e;
                border: none;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QListWidget::item {
                color: #ecf0f1;
                padding: 15px;
            }
            QListWidget::item:selected {
                background-color: #2980b9;
                color: white;
                border-left: 3px solid #3498db;
            }
            QStackedWidget > QWidget {
                background-color: #ecf0f1;
            }
            QLabel#pageTitle {
                font-family: 'Segoe UI', sans-serif;
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QPushButton#addButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton#addButton:hover {
                background-color: #2ecc71;
            }
        """