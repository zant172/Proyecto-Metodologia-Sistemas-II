from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime
from ..dashboard_logic import get_recent_expenses, create_expense

class ExpensesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QVBoxLayout()
        title = QLabel("Gestión de Gastos")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Registra y controla los egresos del negocio")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Layout principal con dos columnas
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        
        # Columna Izquierda: Formulario
        form_panel = self.create_form_panel()
        main_layout.addWidget(form_panel, 1) # Ocupa 1/3 del espacio
        
        # Columna Derecha: Lista
        list_panel = self.create_list_panel()
        main_layout.addWidget(list_panel, 2) # Ocupa 2/3 del espacio
        
        layout.addLayout(main_layout)
    
    def create_form_panel(self):
        panel = QFrame()
        panel.setObjectName("metricCard") # Estilo de tarjeta
        layout = QVBoxLayout(panel)
        
        title = QLabel("Registrar Nuevo Gasto")
        title.setObjectName("metricTitle") # Estilo de título de tarjeta
        layout.addWidget(title)
        
        # Usamos QFormLayout para alinear labels y inputs
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 15, 0, 0) # Espacio arriba
        form_layout.setVerticalSpacing(15) # Espacio entre filas
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Ej: Pago de alquiler")
        form_layout.addRow("Descripción:", self.description_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.amount_input.setPrefix("$ ") # Añadimos prefijo de moneda
        form_layout.addRow("Monto:", self.amount_input)
        
        self.category_combo = QComboBox()
        # Añadimos categorías de ejemplo (podrían venir de la BD en el futuro)
        self.category_combo.addItems(['Seleccionar categoría', 'Servicios', 'Suministros', 'Marketing', 'Mantenimiento', 'Salarios', 'Impuestos', 'Otros'])
        form_layout.addRow("Categoría:", self.category_combo)
        
        layout.addLayout(form_layout)
        
        # Botón de registro
        submit_btn = QPushButton("Registrar Gasto")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self.add_expense)
        # Layout para alinear el botón a la derecha
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(submit_btn)
        layout.addLayout(button_layout)
        
        layout.addStretch() # Empuja el formulario hacia arriba
        return panel
    
    def create_list_panel(self):
        panel = QFrame()
        panel.setObjectName("metricCard") # Estilo de tarjeta
        layout = QVBoxLayout(panel)
        
        title = QLabel("Últimos Gastos Registrados")
        title.setObjectName("metricTitle") # Estilo de título de tarjeta
        layout.addWidget(title)
        
        # ScrollArea para la lista
        self.expenses_scroll = QScrollArea()
        self.expenses_scroll.setWidgetResizable(True)
        # Hacemos transparente para que tome el fondo de la tarjeta
        self.expenses_scroll.setStyleSheet("background: transparent; border: none;") 
        self.expenses_widget = QWidget()
        self.expenses_widget.setStyleSheet("background: transparent;")
        self.expenses_layout = QVBoxLayout(self.expenses_widget)
        self.expenses_layout.setContentsMargins(0, 10, 0, 0) # Espacio arriba
        self.expenses_scroll.setWidget(self.expenses_widget)
        
        layout.addWidget(self.expenses_scroll)
        return panel
    
    def refresh_data(self):
        # Método llamado por MainWindow al cambiar de pestaña
        self.update_expenses_list()

    def update_expenses_list(self):
        # Limpia la lista anterior
        while self.expenses_layout.count():
            item = self.expenses_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Obtiene gastos recientes de la base de datos
        expenses, error = get_recent_expenses()
        
        if error:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudieron cargar los gastos: {error}")
            msg.exec()
            return
        
        if not expenses:
            empty_label = QLabel("No hay gastos registrados")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.expenses_layout.addWidget(empty_label)
        
        # Muestra cada gasto
        for expense in expenses:
            expense_frame = QFrame()
            # Estilo sutil para cada gasto en la lista
            expense_frame.setStyleSheet("border-bottom: 1px solid rgba(100, 116, 139, 0.2); padding: 10px 0;") 
            
            expense_layout = QHBoxLayout(expense_frame)
            
            # Icono (opcional, ejemplo con emoji)
            icon_label = QLabel("💸") 
            icon_label.setFixedWidth(30)
            
            # Información del gasto
            info_layout = QVBoxLayout()
            desc_label = QLabel(expense.Descripcion)
            desc_label.setStyleSheet("font-weight: bold;")
            
            # Usamos 'Categoria' si existe, si no 'Otros'
            category_text = getattr(expense, 'Categoria', 'Otros') 
            details_label = QLabel(f"{category_text} • {expense.FechaGasto.strftime('%Y-%m-%d')}")
            details_label.setStyleSheet("font-size: 12px; color: #94A3B8;")
            
            info_layout.addWidget(desc_label)
            info_layout.addWidget(details_label)
            
            # Monto del gasto (en rojo)
            amount_label = QLabel(f"-${expense.Monto:.2f}")
            amount_label.setStyleSheet("font-weight: bold; color: #F87171;") # Rojo del QSS
            
            # Ensamblamos el layout del item
            expense_layout.addWidget(icon_label)
            expense_layout.addLayout(info_layout, 1)
            expense_layout.addWidget(amount_label)
            
            self.expenses_layout.addWidget(expense_frame)
        
        self.expenses_layout.addStretch() # Empuja items hacia arriba
    
    def add_expense(self):
        description = self.description_input.text().strip()
        amount = self.amount_input.value()
        category = self.category_combo.currentText()
        
        if not description or amount <= 0 or category == 'Seleccionar categoría':
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Campos Incompletos")
            msg.setText("Por favor completa todos los campos correctamente.")
            msg.exec()
            return
        
        # Llama a la función de lógica para crear el gasto
        success, message = create_expense(description, amount, category)
        
        msg = QMessageBox(self)
        if success:
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Gasto Registrado")
            msg.setText("Gasto registrado correctamente.")
            msg.exec()
            # Limpia el formulario
            self.description_input.clear()
            self.amount_input.setValue(0.01) # Resetea al mínimo
            self.category_combo.setCurrentIndex(0)
            # Actualiza la lista de gastos
            self.refresh_data()
        else:
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(message)
            msg.exec()