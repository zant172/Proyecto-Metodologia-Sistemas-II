import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QListWidget,
                             QStackedWidget, QListWidgetItem, QLabel, QVBoxLayout)
from PyQt6.QtCore import Qt
from .pages.dashboard_page import DashboardWidget
from .pages.products_page import InventoryWidget
from .pages.sales_page import POSWidget
from .pages.reports_page import ReportsWidget
from .pages.expenses_page import ExpensesWidget
from .pages.users_page import UsersWidget
# Importa las nuevas páginas
from .pages.caja_page import CajaWidget
from .pages.metodos_pago_page import MetodosPagoWidget


class MainWindow(QMainWindow):
    def __init__(self, user_role, user_id):
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.setWindowTitle("Sistema Gestion Ventas JG")
        self.setMinimumSize(1200, 800)
        self.showMaximized()

        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_bar = QListWidget()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setFixedWidth(250)
        main_layout.addWidget(self.nav_bar)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.create_pages()
        self.nav_bar.currentItemChanged.connect(self.on_nav_item_changed)
        self.setup_ui_for_role()

        first_visible_row = -1
        for i in range(self.nav_bar.count()):
             if not self.nav_bar.item(i).isHidden(): first_visible_row = i; break
        if first_visible_row != -1: self.nav_bar.setCurrentRow(first_visible_row)
        elif self.nav_bar.count() > 0: self.nav_bar.setCurrentRow(0)

    def create_pages(self):
        self.pages_config = {
            "📊 Dashboard": DashboardWidget,
            "📦 Inventario": InventoryWidget,
            "💳 Punto de Venta": POSWidget,
            "💰 Gastos": ExpensesWidget,
            "📈 Reportes": ReportsWidget,
            "🔒 Cierre de Caja": CajaWidget, # Nueva página
            "⚙️ Métodos de Pago": MetodosPagoWidget, # Nueva página
            "👥 Gestión Usuarios": UsersWidget
        }
        for name, PageWidgetClass in self.pages_config.items():
            item = QListWidgetItem(name)
            self.nav_bar.addItem(item)
            try:
                page_args = {}
                # Pasa user_id o user_role a las páginas que lo necesitan
                if name in ["💳 Punto de Venta", "🔒 Cierre de Caja"]:
                    page_args['user_id'] = self.user_id
                if name in ["👥 Gestión Usuarios"]:
                    page_args['user_role'] = self.user_role
                
                page = PageWidgetClass(**page_args) if page_args else PageWidgetClass()

            except Exception as e:
                print(f"❌ Error instanciando {name}: {e}")
                page = QWidget(); page.setLayout(QVBoxLayout()); err_label = QLabel(f"Error:\n{name}\n\n{e}"); err_label.setAlignment(Qt.AlignmentFlag.AlignCenter); err_label.setStyleSheet("color: red;"); page.layout().addWidget(err_label)
            self.stacked_widget.addWidget(page)

    def on_nav_item_changed(self, current_item):
        if not current_item: return
        index = self.nav_bar.row(current_item)
        self.stacked_widget.setCurrentIndex(index)
        current_page = self.stacked_widget.widget(index)
        if hasattr(current_page, 'refresh_data') and current_page.isEnabled():
            try: current_page.refresh_data()
            except Exception as e: print(f"❌ Error refresh {type(current_page).__name__}: {e}")

    def setup_ui_for_role(self):
        is_user = self.user_role == 'Usuario'
        # Añade las nuevas páginas a la lista de ocultos para 'Usuario'
        items_to_hide = ["📈 Reportes", "💰 Gastos", "👥 Gestión Usuarios", "🔒 Cierre de Caja", "⚙️ Métodos de Pago"] if is_user else []
        
        # El rol 'Admin' debe poder ver todo MENOS el reset de 'Gestión Usuarios' (manejado en la propia página)
        # El rol 'Dev' ve todo
        
        print(f"ℹ️  Rol {self.user_role}. Ocultando: {items_to_hide}" if is_user else f"ℹ️  Rol {self.user_role}. Mostrando todo.")
        for i in range(self.nav_bar.count()):
            item = self.nav_bar.item(i)
            widget = self.stacked_widget.widget(i)
            should_hide = item.text() in items_to_hide
            item.setHidden(should_hide)
            if widget: widget.setEnabled(not should_hide)