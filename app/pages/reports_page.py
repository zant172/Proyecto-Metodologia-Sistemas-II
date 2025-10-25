from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit
from PyQt6.QtCore import QDate
from ..dashboard_logic import get_reports_data

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__(); layout = QVBoxLayout(self)
        title = QLabel("Reportes de Ventas"); title.setObjectName("pageTitle"); layout.addWidget(title)
        filter_layout = QHBoxLayout(); filter_layout.addWidget(QLabel("Desde:"))
        self.start_date = QDateEdit(calendarPopup=True); self.start_date.setDate(QDate.currentDate().addMonths(-1)); filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Hasta:")); self.end_date = QDateEdit(calendarPopup=True); self.end_date.setDate(QDate.currentDate()); filter_layout.addWidget(self.end_date)
        self.generate_btn = QPushButton("Generar Reporte"); filter_layout.addWidget(self.generate_btn); filter_layout.addStretch(); layout.addLayout(filter_layout)
        self.table = QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["ID Venta", "Fecha", "Vendedor", "Total"])
        self.table.verticalHeader().setVisible(False); self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents); header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table); self.generate_btn.clicked.connect(self.refresh_data)

    def refresh_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd"); end = self.end_date.date().toString("yyyy-MM-dd")
        data, error = get_reports_data(start, end)
        if error: QMessageBox.critical(self, "Error", f"No se pudo generar reporte: {error}"); self.table.setRowCount(0); return
        self.table.setRowCount(len(data))
        for r, rec in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(rec.idVenta))); self.table.setItem(r, 1, QTableWidgetItem(rec.FechaVenta.strftime('%Y-%m-%d %H:%M')))
            self.table.setItem(r, 2, QTableWidgetItem(rec.Usuario)); self.table.setItem(r, 3, QTableWidgetItem(f"${rec.Total:.2f}"))

    def update_theme(self, is_dark): pass