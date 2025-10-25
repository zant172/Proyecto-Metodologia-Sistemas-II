from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QStackedWidget, QListWidgetItem, QPushButton, QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from .pages.dashboard_page import DashboardPage
from .pages.products_page import ProductsPage
from .pages.sales_page import SalesPage
from .pages.users_page import UsersPage
from .pages.reports_page import ReportsPage

class MainWindow(QMainWindow):
    def __init__(self, user_role, user_id):
        super().__init__()
        self.user_role = user_role; self.user_id = user_id
        self.is_dark_mode = "dark-theme" in QApplication.instance().styleSheet() or "#2C3E50" in QApplication.instance().styleSheet()
        self.setWindowTitle("InfinityTech - Sistema de Gestión"); self.setMinimumSize(1200, 800)
        main_layout = QHBoxLayout(); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)
        central_widget = QWidget(); central_widget.setLayout(main_layout); self.setCentralWidget(central_widget)
        left_panel = QWidget(); left_panel.setFixedWidth(200); left_panel.setObjectName("leftPanel")
        left_panel_layout = QVBoxLayout(left_panel); left_panel_layout.setContentsMargins(0, 0, 0, 0); left_panel_layout.setSpacing(0)
        self.title_label = QLabel("InfinityTech\nSistema de Gestión"); self.title_label.setObjectName("navBarTitle"); self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel_layout.addWidget(self.title_label)
        self.nav_bar = QListWidget(); self.nav_bar.setIconSize(QSize(24, 24)); self.nav_bar.setObjectName("navBar")
        left_panel_layout.addWidget(self.nav_bar, 1)
        self.theme_toggle_button = QPushButton(); self.theme_toggle_button.setObjectName("themeToggleButton"); self.theme_toggle_button.setIconSize(QSize(24, 24)); self.theme_toggle_button.setFixedHeight(40)
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        left_panel_layout.addWidget(self.theme_toggle_button)
        main_layout.addWidget(left_panel)
        self.stacked_widget = QStackedWidget(); main_layout.addWidget(self.stacked_widget, 1)
        self.create_pages(); self.setup_theme()
        self.nav_bar.currentItemChanged.connect(self.on_nav_item_changed); self.setup_ui_for_role()
        if self.nav_bar.count() > 0: self.nav_bar.setCurrentRow(0)

    def create_pages(self):
        self.pages_config = {
            "Inicio": (DashboardPage, "app/icons/home-dark.svg", "app/icons/home-light.svg"),
            "Productos": (ProductsPage, "app/icons/package-dark.svg", "app/icons/package-light.svg"),
            "Punto de Venta": (SalesPage, "app/icons/shopping-cart-dark.svg", "app/icons/shopping-cart-light.svg"),
            "Gestión de Usuarios": (UsersPage, "app/icons/users-dark.svg", "app/icons/users-light.svg"),
            "Reportes": (ReportsPage, "app/icons/bar-chart-2-dark.svg", "app/icons/bar-chart-2-light.svg")}
        for name, (PageWidgetClass, icon_light, icon_dark) in self.pages_config.items():
            item = QListWidgetItem(name); item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            item.setData(Qt.ItemDataRole.UserRole + 1, icon_light); item.setData(Qt.ItemDataRole.UserRole + 2, icon_dark)
            self.nav_bar.addItem(item)
            page = PageWidgetClass(user_id=self.user_id) if name == "Punto de Venta" else PageWidgetClass()
            self.stacked_widget.addWidget(page)

    def on_nav_item_changed(self, current_item):
        if not current_item: return
        index = self.nav_bar.row(current_item); self.stacked_widget.setCurrentIndex(index)
        current_page = self.stacked_widget.widget(index)
        if hasattr(current_page, 'refresh_data'): current_page.refresh_data()

    def setup_ui_for_role(self):
        if self.user_role == 'Usuario':
            for i in range(self.nav_bar.count()):
                item = self.nav_bar.item(i)
                if item.text() in ["Gestión de Usuarios", "Reportes"]: item.setHidden(True)

    def setup_theme(self): self.update_theme_icons()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        theme_file = "dark-theme.qss" if self.is_dark_mode else "light-theme.qss"
        try:
            with open(theme_file, "r", encoding="utf-8") as f: QApplication.instance().setStyleSheet(f.read())
            self.update_theme_icons(); self.broadcast_theme_change()
        except Exception as e: print(f"Error al cargar tema {theme_file}: {e}")

    def update_theme_icons(self):
        self.theme_toggle_button.setIcon(QIcon("app/icons/sun.svg" if self.is_dark_mode else "app/icons/moon.svg"))
        for i in range(self.nav_bar.count()):
            item = self.nav_bar.item(i)
            icon_path = item.data(Qt.ItemDataRole.UserRole + 2) if self.is_dark_mode else item.data(Qt.ItemDataRole.UserRole + 1)
            if icon_path:
                try: item.setIcon(QIcon(icon_path))
                except Exception as e: print(f"Error al actualizar ícono {icon_path}: {e}")

    def broadcast_theme_change(self):
        for i in range(self.stacked_widget.count()):
            page = self.stacked_widget.widget(i)
            if hasattr(page, 'update_theme'):
                try: page.update_theme(self.is_dark_mode)
                except Exception as e: print(f"Error al actualizar tema en página {i}: {e}")