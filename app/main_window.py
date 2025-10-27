from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QListWidget, QStackedWidget, QListWidgetItem)
from PyQt6.QtCore import Qt

# Asegúrate de importar las clases correctas de tus archivos de páginas
from .pages.dashboard_page import DashboardWidget
from .pages.products_page import InventoryWidget
from .pages.sales_page import POSWidget
from .pages.reports_page import ReportsWidget
from .pages.expenses_page import ExpensesWidget
from .pages.users_page import UsersWidget

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
        self.nav_bar.setObjectName("navBar") # Importante para el style.qss
        self.nav_bar.setFixedWidth(250) 
        main_layout.addWidget(self.nav_bar)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.create_pages()
        
        self.nav_bar.currentItemChanged.connect(self.on_nav_item_changed)
        
        self.setup_ui_for_role()
        if self.nav_bar.count() > 0:
            self.nav_bar.setCurrentRow(0)

    def create_pages(self):
        
        self.pages_config = {
            "📊 Dashboard": DashboardWidget,
            "📦 Inventario": InventoryWidget,
            "💳 Punto de Venta": POSWidget,
            "📈 Reportes": ReportsWidget,
            "💰 Gastos": ExpensesWidget,
            "👥 Gestión Usuarios": UsersWidget
        }

        for name, PageWidgetClass in self.pages_config.items():
            
            item = QListWidgetItem(name)
            # El style.qss se encarga del centrado y estilo
            self.nav_bar.addItem(item)
            
            # Asegúrate de que tus clases acepten user_id si lo necesitan
            if name == "💳 Punto de Venta":
                page = PageWidgetClass(user_id=self.user_id)
            else:
                try: # Intenta crear sin user_id
                    page = PageWidgetClass()
                except TypeError: # Si falla, es porque necesita user_id (ajusta si es necesario)
                    page = PageWidgetClass(user_id=self.user_id) 

            self.stacked_widget.addWidget(page)
        
    def on_nav_item_changed(self, current_item):
        if not current_item: return
        index = self.nav_bar.row(current_item)
        self.stacked_widget.setCurrentIndex(index)
        
        current_page = self.stacked_widget.widget(index)
        if hasattr(current_page, 'refresh_data'):
            current_page.refresh_data()

    def setup_ui_for_role(self):
        if self.user_role == 'Usuario':
            items_to_hide = ["📈 Reportes", "💰 Gastos", "👥 Gestión Usuarios"]
            for i in range(self.nav_bar.count()):
                item = self.nav_bar.item(i)
                if item.text() in items_to_hide:
                    # Oculta el item del menú
                    item.setHidden(True)
                    # Deshabilita la página correspondiente para seguridad
                    corresponding_widget = self.stacked_widget.widget(i)
                    if corresponding_widget:
                         corresponding_widget.setEnabled(False)