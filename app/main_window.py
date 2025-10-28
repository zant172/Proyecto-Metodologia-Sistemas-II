import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QListWidget,
                             QStackedWidget, QListWidgetItem, QLabel, QVBoxLayout)
from PyQt6.QtCore import Qt
# Importa TODAS las clases de tus páginas
from .pages.dashboard_page import DashboardWidget
from .pages.products_page import InventoryWidget
from .pages.sales_page import POSWidget
from .pages.reports_page import ReportsWidget
from .pages.expenses_page import ExpensesWidget
from .pages.users_page import UsersWidget

class MainWindow(QMainWindow):
    def __init__(self, user_role, user_id):
        super().__init__()
        self.user_role = user_role # Guarda el rol ('Dev', 'Admin', 'Usuario')
        self.user_id = user_id     # Guarda el ID del usuario logueado
        self.setWindowTitle("InfinityTech - Sistema de Gestión")
        self.setMinimumSize(1200, 800) # Tamaño mínimo
        self.showMaximized() # Inicia maximizada

        # Configuración del layout principal (Horizontal: Sidebar | Contenido)
        main_layout = QHBoxLayout()
        central_widget = QWidget() # Widget contenedor central
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes externos
        main_layout.setSpacing(0) # Sin espacio entre sidebar y contenido

        # Barra lateral de navegación (QListWidget)
        self.nav_bar = QListWidget()
        self.nav_bar.setObjectName("navBar") # ID para aplicar estilo desde style.qss
        self.nav_bar.setFixedWidth(250)      # Ancho fijo para la barra lateral
        main_layout.addWidget(self.nav_bar) # Añade la barra al layout principal

        # Contenedor de páginas (QStackedWidget)
        self.stacked_widget = QStackedWidget()
        # El estilo de padding y fondo se aplica desde style.qss a los hijos
        main_layout.addWidget(self.stacked_widget) # Añade el stack al layout

        # Crea las páginas y los items del menú lateral
        self.create_pages()
        # Conecta la señal de cambio de item a la función que cambia la página visible
        self.nav_bar.currentItemChanged.connect(self.on_nav_item_changed)
        # Oculta/Deshabilita opciones según el rol
        self.setup_ui_for_role()

        # Selecciona la primera opción (Dashboard) al iniciar si hay items
        if self.nav_bar.count() > 0 and self.nav_bar.item(0).isHidden() is False:
             self.nav_bar.setCurrentRow(0)
        # Si el primer item está oculto, busca el primero visible
        elif self.nav_bar.count() > 0:
             for i in range(self.nav_bar.count()):
                  if not self.nav_bar.item(i).isHidden():
                       self.nav_bar.setCurrentRow(i)
                       break


    def create_pages(self):
        # Diccionario que mapea el texto del menú a la clase de la página
        self.pages_config = {
            "📊 Dashboard": DashboardWidget,
            "📦 Inventario": InventoryWidget,
            "💳 Punto de Venta": POSWidget,
            "📈 Reportes": ReportsWidget,
            "💰 Gastos": ExpensesWidget,
            "👥 Gestión Usuarios": UsersWidget
        }

        # Itera para crear cada item del menú y su página correspondiente
        for name, PageWidgetClass in self.pages_config.items():
            # Crea el item visual para el QListWidget
            item = QListWidgetItem(name)
            # El estilo (color, padding, hover, selected) lo aplica style.qss
            self.nav_bar.addItem(item)

            # Intenta crear la instancia de la página
            try:
                # Pasa user_id específicamente a POSWidget (y otras si lo necesitan)
                if name == "💳 Punto de Venta":
                    page = PageWidgetClass(user_id=self.user_id)
                else: # Para las demás, intenta crear sin argumentos
                    page = PageWidgetClass()
            except Exception as e:
                # Si falla la creación (ej. error en __init__ de la página), muestra un error
                print(f"❌ Error al instanciar página '{name}': {e}")
                # Crea un widget placeholder con el mensaje de error
                page = QWidget()
                page.setLayout(QVBoxLayout())
                error_label = QLabel(f"Error al cargar módulo:\n{name}\n\n{e}")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet("color: red;") # Estilo simple para error
                page.layout().addWidget(error_label)

            # Añade la página (o el placeholder de error) al QStackedWidget
            self.stacked_widget.addWidget(page)

    def on_nav_item_changed(self, current_item):
        # Se llama automáticamente cuando el usuario clica un item diferente en nav_bar
        if not current_item: return # Evita error si se deselecciona todo
        index = self.nav_bar.row(current_item) # Obtiene el índice (0, 1, 2...) del item
        # Cambia la página visible en el QStackedWidget a la que corresponde a ese índice
        self.stacked_widget.setCurrentIndex(index)

        # Llama al método 'refresh_data' de la página recién mostrada, si existe
        # Esto permite que la página actualice sus datos (ej. recargar tabla)
        current_page = self.stacked_widget.widget(index)
        if hasattr(current_page, 'refresh_data'):
            try:
                # print(f"Llamando refresh_data en {type(current_page).__name__}") # Log
                current_page.refresh_data()
            except Exception as e:
                # Captura y loguea errores que ocurran DENTRO de refresh_data
                print(f"❌ Error durante refresh_data en {type(current_page).__name__}: {e}")
                # Podríamos mostrar un QMessageBox aquí si el error es grave

    def setup_ui_for_role(self):
        # Oculta opciones del menú y deshabilita páginas según el rol 'Usuario'
        if self.user_role == 'Usuario':
            # Define qué items/páginas ocultar para el rol 'Usuario'
            items_to_hide = ["📈 Reportes", "💰 Gastos", "👥 Gestión Usuarios"]
            print(f"ℹ️  Rol Usuario detectado. Ocultando: {items_to_hide}")
            for i in range(self.nav_bar.count()): # Recorre todos los items del menú
                item = self.nav_bar.item(i)
                if item.text() in items_to_hide:
                    print(f" -> Ocultando item: {item.text()}")
                    item.setHidden(True) # Oculta el item en QListWidget
                    # También deshabilita el widget correspondiente en QStackedWidget
                    corresponding_widget = self.stacked_widget.widget(i)
                    if corresponding_widget:
                        corresponding_widget.setEnabled(False) # La página no será accesible