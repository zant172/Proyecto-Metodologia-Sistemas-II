from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from .metric_card import MetricCard
from ..dashboard_logic import get_dashboard_metrics, get_chart_data

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__(); main_layout = QVBoxLayout(self)
        title = QLabel("Dashboard"); title.setObjectName("pageTitle"); main_layout.addWidget(title)
        cards_layout = QHBoxLayout()
        self.card_ventas = MetricCard("Ventas (Mes)", "$0.00", "green"); self.card_gastos = MetricCard("Gastos (Mes)", "$0.00", "red")
        self.card_balance = MetricCard("Balance Neto", "$0.00", "blue"); self.card_stock = MetricCard("Alertas Stock Bajo", "0", "orange")
        cards_layout.addWidget(self.card_ventas); cards_layout.addWidget(self.card_gastos); cards_layout.addWidget(self.card_balance); cards_layout.addWidget(self.card_stock)
        main_layout.addLayout(cards_layout)
        chart_widget = QWidget(); chart_layout = QVBoxLayout(chart_widget); chart_widget.setObjectName("metricCard")
        chart_title = QLabel("Ventas - Últimos 7 días"); chart_title.setObjectName("metricTitle"); chart_layout.addWidget(chart_title)
        self.plot_widget = pg.PlotWidget(); self.plot_widget.setMinimumHeight(400); self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.chart = pg.BarGraphItem(x=[], height=[], width=0.6, brush='#3498db'); self.plot_widget.addItem(self.chart)
        chart_layout.addWidget(self.plot_widget); main_layout.addWidget(chart_widget); main_layout.addStretch()
        self.update_theme(False)

    def refresh_data(self):
        try:
            metrics = get_dashboard_metrics()
            self.card_ventas.set_value(metrics.get("ventas_mes", "$0.00")); self.card_gastos.set_value(metrics.get("gastos_mes", "$0.00"))
            self.card_balance.set_value(metrics.get("balance_mes", "$0.00")); self.card_stock.set_value(metrics.get("stock_bajo", "0"))
            labels, values = get_chart_data()
            ticks = [list(enumerate(labels))] if labels and values else None
            x_vals = list(range(len(values))) if values else []
            self.plot_widget.getAxis('bottom').setTicks(ticks); self.chart.setOpts(x=x_vals, height=values)
        except Exception as e: QMessageBox.warning(self, "Error Dashboard", f"No se cargaron datos: {e}")

    def update_theme(self, is_dark):
        bg = '#34495E' if is_dark else 'w'; pen = QPen(Qt.GlobalColor.white if is_dark else Qt.GlobalColor.black)
        self.plot_widget.setBackground(bg); self.plot_widget.getAxis('bottom').setTextPen(pen); self.plot_widget.getAxis('left').setTextPen(pen)