from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..dashboard_logic import get_reports_data

class SalesTableWidget(QTableWidget):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.setup_table()
    
    def setup_table(self):
        self.setColumnCount(4) # ID, Fecha, Vendedor, Total
        self.setHorizontalHeaderLabels(['ID Venta', 'Fecha', 'Vendedor', 'Total'])
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents) # ID y Fecha se ajustan
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Vendedor toma espacio
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) # Total toma espacio
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
    
    def load_report_data(self, start_date, end_date):
        data, error = get_reports_data(start_date, end_date)
        
        if error:
            msg = QMessageBox(self.parent_widget)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudo generar el reporte: {error}")
            msg.exec()
            self.setRowCount(0)
            return

        self.setRowCount(len(data))
        for row, record in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(str(record.idVenta)))
            self.setItem(row, 1, QTableWidgetItem(record.FechaVenta.strftime('%Y-%m-%d %H:%M')))
            self.setItem(row, 2, QTableWidgetItem(record.Usuario))
            
            total_item = QTableWidgetItem(f"${record.Total:.2f}")
            # Podemos darle un estilo especial al total si queremos
            # total_item.setForeground(QColor('#10B981')) # Verde del QSS
            self.setItem(row, 3, total_item)

class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QVBoxLayout()
        title = QLabel("Reportes")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Analiza el rendimiento de tu negocio")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Controles de fecha y botones
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 20)
        
        controls_layout.addWidget(QLabel("Desde:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1)) # Un mes atrás por defecto
        self.from_date.setCalendarPopup(True)
        # Forzamos el estilo del QSS porque QDateEdit a veces lo ignora
        self.from_date.setStyleSheet("""
            QDateEdit {
                background: rgba(51, 65, 85, 0.5);
                border: 2px solid rgba(100, 116, 139, 0.3);
                border-radius: 12px;
                padding: 14px 16px;
                font-size: 15px;
                color: #F1F5F9;
            }
            QDateEdit:focus { border: 2px solid #6366F1; }
            QDateEdit:hover { border: 2px solid rgba(99, 102, 241, 0.5); }
            QDateEdit::drop-down { border: none; width: 30px; }
            QDateEdit::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #94A3B8; margin-right: 8px; }
        """)

        controls_layout.addWidget(self.from_date)
        controls_layout.addWidget(QLabel("Hasta:"))
        
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        self.to_date.setStyleSheet(self.from_date.styleSheet()) # Reusamos el estilo

        controls_layout.addWidget(self.to_date)
        
        generate_btn = QPushButton("Generar Reporte")
        generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        generate_btn.clicked.connect(self.refresh_data)
        
        export_btn = QPushButton("Exportar a Excel")
        export_btn.setObjectName("addButton") # Estilo verde
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Añadir funcionalidad de exportar aquí si se desea
        
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Tabla de ventas
        self.sales_table = SalesTableWidget(self)
        layout.addWidget(self.sales_table)
        
        # Cargamos datos iniciales al abrir
        self.refresh_data() 
    
    def refresh_data(self):
        # Obtiene fechas seleccionadas y carga datos en la tabla
        start_date = self.from_date.date().toString("yyyy-MM-dd")
        end_date = self.to_date.date().toString("yyyy-MM-dd")
        self.sales_table.load_report_data(start_date, end_date)