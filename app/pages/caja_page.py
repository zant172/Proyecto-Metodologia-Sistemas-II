from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime
from ..dashboard_logic import get_resumen_dia_actual, check_cierre_realizado_hoy, get_historial_cierres, perform_cierre_caja

class CajaWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Cierre de Caja Diario"); title.setObjectName("pageTitle")
        subtitle = QLabel("Revisa las operaciones del día y realiza el cierre.")
        layout.addWidget(title); layout.addWidget(subtitle)
        
        main_layout = QHBoxLayout(); main_layout.setSpacing(20)
        
        resumen_panel = self.create_resumen_panel()
        main_layout.addWidget(resumen_panel, 1)
        
        historial_panel = self.create_historial_panel()
        main_layout.addWidget(historial_panel, 2)
        
        layout.addLayout(main_layout)

    def create_resumen_panel(self):
        panel = QFrame(); panel.setObjectName("metricCard"); layout = QVBoxLayout(panel)
        
        title = QLabel("Resumen del Día (Hoy)"); title.setObjectName("metricTitle")
        layout.addWidget(title)
        
        self.resumen_layout = QFormLayout(); self.resumen_layout.setContentsMargins(0, 15, 0, 0)
        self.ventas_total_label = QLabel("$0.00"); self.ventas_total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #10B981;")
        self.gastos_total_label = QLabel("$0.00"); self.gastos_total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #F87171;")
        self.balance_neto_label = QLabel("$0.00"); self.balance_neto_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #6366F1;")
        
        self.resumen_layout.addRow("Total Ventas:", self.ventas_total_label)
        
        # Layout para el desglose de ventas
        self.desglose_ventas_widget = QWidget(); self.desglose_ventas_layout = QVBoxLayout(self.desglose_ventas_widget)
        self.desglose_ventas_layout.setContentsMargins(10, 5, 0, 10)
        self.resumen_layout.addRow(self.desglose_ventas_widget)
        
        self.resumen_layout.addRow("Total Gastos:", self.gastos_total_label)
        self.resumen_layout.addRow("Balance Neto (Ventas - Gastos):", self.balance_neto_label)
        layout.addLayout(self.resumen_layout)
        
        layout.addStretch()
        
        self.cierre_status_label = QLabel("Estado: Verificando...")
        self.cierre_status_label.setStyleSheet("font-style: italic; color: #94A3B8;")
        layout.addWidget(self.cierre_status_label)
        
        self.cierre_button = QPushButton("Realizar Cierre de Caja"); self.cierre_button.setObjectName("finalizeButton")
        self.cierre_button.setCursor(Qt.CursorShape.PointingHandCursor); self.cierre_button.clicked.connect(self.handle_perform_cierre)
        layout.addWidget(self.cierre_button)
        return panel

    def create_historial_panel(self):
        panel = QFrame(); panel.setObjectName("metricCard"); layout = QVBoxLayout(panel)
        title = QLabel("Historial de Cierres"); title.setObjectName("metricTitle"); layout.addWidget(title)
        self.historial_table = QTableWidget()
        self.historial_table.setColumnCount(5)
        self.historial_table.setHorizontalHeaderLabels(["Fecha Cierre", "Usuario", "Total Ventas", "Total Gastos", "Balance Neto"])
        header = self.historial_table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents); header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.historial_table.verticalHeader().setVisible(False); self.historial_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.historial_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.historial_table.setShowGrid(False)
        layout.addWidget(self.historial_table)
        return panel

    def refresh_data(self):
        self.load_resumen_hoy()
        self.load_historial_cierres()

    def load_resumen_hoy(self):
        is_cerrado, msg_cerrado = check_cierre_realizado_hoy()
        if is_cerrado:
            self.cierre_status_label.setText(f"Estado: {msg_cerrado}")
            self.cierre_button.setEnabled(False); self.cierre_button.setText("Caja de Hoy Cerrada")
        else:
            self.cierre_status_label.setText(f"Estado: {msg_cerrado}")
            self.cierre_button.setEnabled(True); self.cierre_button.setText("Realizar Cierre de Caja")
            
        resumen, error = get_resumen_dia_actual()
        if error:
            QMessageBox.critical(self, "Error Resumen", f"No se pudo cargar el resumen: {error}")
            return
            
        self.ventas_total_label.setText(f"${resumen['ventas_total']:.2f}")
        self.gastos_total_label.setText(f"${resumen['gastos_total']:.2f}")
        self.balance_neto_label.setText(f"${resumen['balance_neto']:.2f}")

        # Limpiar desglose anterior
        while self.desglose_ventas_layout.count():
            item = self.desglose_ventas_layout.takeAt(0); widget = item.widget()
            if widget: widget.deleteLater()
            
        if not resumen['ventas_desglose']:
             lbl = QLabel("Sin ventas registradas hoy."); lbl.setStyleSheet("font-size: 12px; color: #94A3B8;"); self.desglose_ventas_layout.addWidget(lbl)
        else:
            for (metodo, total) in resumen['ventas_desglose']:
                 # Convertir total a float si es Decimal para evitar errores de formato
                 total_float = float(total) if hasattr(total, '__float__') else total
                 lbl_text = f"  • {metodo}: ${total_float:.2f}"
                 lbl = QLabel(lbl_text); lbl.setStyleSheet("font-size: 13px; color: #CBD5E1;"); self.desglose_ventas_layout.addWidget(lbl)
        self.desglose_ventas_layout.addStretch()

    def load_historial_cierres(self):
        data, error = get_historial_cierres()
        if error:
             QMessageBox.critical(self, "Error Historial", f"No se pudo cargar el historial: {error}"); self.historial_table.setRowCount(0); return
        self.historial_table.setRowCount(len(data))
        for row, record in enumerate(data):
            self.historial_table.setItem(row, 0, QTableWidgetItem(record.FechaCierre.strftime('%Y-%m-%d')))
            self.historial_table.setItem(row, 1, QTableWidgetItem(record.NombreCompleto))
            self.historial_table.setItem(row, 2, QTableWidgetItem(f"${record.TotalVentas:.2f}"))
            self.historial_table.setItem(row, 3, QTableWidgetItem(f"${record.TotalGastos:.2f}"))
            self.historial_table.setItem(row, 4, QTableWidgetItem(f"${record.BalanceNeto:.2f}"))
            # Colorear balance
            if record.BalanceNeto < 0: self.historial_table.item(row, 4).setForeground(QColor("#F87171"))
            else: self.historial_table.item(row, 4).setForeground(QColor("#10B981"))

    def handle_perform_cierre(self):
        confirm = QMessageBox.question(self, "Confirmar Cierre",
                                       "¿Está seguro de realizar el cierre de caja?\n"
                                       "Esta acción es permanente y solo se puede hacer una vez al día.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No: return
        
        success, message = perform_cierre_caja(self.user_id)
        
        msg = QMessageBox(self)
        if success:
            msg.setIcon(QMessageBox.Icon.Information); msg.setWindowTitle("Éxito"); msg.setText(message)
            self.refresh_data() # Actualiza la UI para deshabilitar botón y mostrar historial
        else:
            msg.setIcon(QMessageBox.Icon.Critical); msg.setWindowTitle("Error"); msg.setText(message)
        msg.exec()