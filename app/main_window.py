from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QListWidget, QStackedWidget, QListWidgetItem)
from PyQt6.QtCore import Qt

from .pages.dashboard_page import DashboardPage
from .pages.products_page import ProductsPage
from .pages.sales_page import SalesPage
from .pages.users_page import UsersPage
from .pages.reports_page import ReportsPage

class MainWindow(QMainWindow):
    def __init__(self, user_role, user_id):
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        
        self.setWindowTitle("InfinityTech - Sistema de Gestión")
        self.setMinimumSize(1200, 800)
        self.showMaximized()

        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.nav_bar = QListWidget()
        self.nav_bar.setFixedWidth(200)
        self.nav_bar.setObjectName("navBar")
        main_layout.addWidget(self.nav_bar)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.create_pages()
        
        self.nav_bar.currentItemChanged.connect(self.on_nav_item_changed)
        
        self.setup_ui_for_role()
        self.nav_bar.setCurrentRow(0)

    def create_pages(self):
        
        self.pages_config = {
            "🏠 Inicio": DashboardPage,
            "📦 Productos": ProductsPage,
            "🛒 Punto de Venta": SalesPage,
            "👥 Gestión de Usuarios": UsersPage,
            "📊 Reportes": ReportsPage
        }

        for name, PageWidgetClass in self.pages_config.items():
            
            item = QListWidgetItem(name)
            
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.nav_bar.addItem(item)
            
            if name == "🛒 Punto de Venta":
                page = PageWidgetClass(user_id=self.user_id)
            else:
                page = PageWidgetClass()
                
            self.stacked_widget.addWidget(page)
        
    def on_nav_item_changed(self, current_item):
        index = self.nav_bar.row(current_item)
        self.stacked_widget.setCurrentIndex(index)
        
        current_page = self.stacked_widget.widget(index)
        if hasattr(current_page, 'refresh_data'):
            current_page.refresh_data()

    def setup_ui_for_role(self):
        if self.user_role == 'Usuario':
            for i in range(self.nav_bar.count()):
                item = self.nav_bar.item(i)
                
                if item.text() in ["👥 Gestión de Usuarios", "📊 Reportes"]:
                    item.setHidden(True)