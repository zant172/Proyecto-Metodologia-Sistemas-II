from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDateEdit)
from PyQt6.QtCore import QDate
from ..dashboard_logic import get_reports_data

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Reportes de Ventas")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Desde:"))
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date_input)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_input)
        
        self.generate_report_button = QPushButton("Generar Reporte")
        filter_layout.addWidget(self.generate_report_button)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(["ID Venta", "Fecha", "Vendedor", "Total"])
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.report_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.report_table)

        self.generate_report_button.clicked.connect(self.refresh_data)
        
        self.refresh_data()

    def refresh_data(self):
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        
        data, error = get_reports_data(start_date, end_date)
        
        if error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte: {error}")
            self.report_table.setRowCount(0)
            return

        self.report_table.setRowCount(len(data))
        for row, record in enumerate(data):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(record.idVenta)))
            self.report_table.setItem(row, 1, QTableWidgetItem(record.FechaVenta.strftime('%Y-%m-%d %H:%M')))
            self.report_table.setItem(row, 2, QTableWidgetItem(record.Usuario))
            self.report_table.setItem(row, 3, QTableWidgetItem(f"${record.Total:.2f}"))