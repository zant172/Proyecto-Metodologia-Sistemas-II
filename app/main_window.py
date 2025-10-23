from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QListWidget, QStackedWidget, QListWidgetItem)
from PyQt6.QtCore import Qt

# Importamos las páginas de nuestro nuevo directorio
from .pages.dashboard_page import DashboardPage # <--- CORRECCIÓN AQUÍ
from .pages.products_page import ProductsPage # <--- CORRECCIÓN AQUÍ
from .pages.sales_page import SalesPage # <--- CORRECCIÓN AQUÍ
from .pages.users_page import UsersPage # <--- CORRECCIÓN AQUÍ
from .pages.reports_page import ReportsPage # <--- CORRECCIÓN AQUÍ

class MainWindow(QMainWindow):
    def __init__(self, user_role):
        super().__init__()
        self.user_role = user_role
        
        self.setWindowTitle("InfinityTech - Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 800)

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
        # Definimos los nombres de los módulos y las clases de widget que les corresponden
        self.pages_config = {
            "Inicio": DashboardPage,
            "Productos": ProductsPage,
            "Punto de Venta": SalesPage,
            "Gestión de Usuarios": UsersPage,
            "Reportes": ReportsPage
        }

        for name, PageWidgetClass in self.pages_config.items():
            # Creamos el item en la barra de navegación
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.nav_bar.addItem(item)
            
            # Creamos una instancia de la página y la añadimos al StackedWidget
            page = PageWidgetClass()
            self.stacked_widget.addWidget(page)
        
    def setup_ui_for_role(self):
        if self.user_role == 'Usuario':
            for i in range(self.nav_bar.count()):
                item = self.nav_bar.item(i)
                if item.text() in ["Gestión de Usuarios", "Reportes"]:
                    item.setHidden(True)