from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from .metric_card import MetricCard
from ..dashboard_logic import get_dashboard_metrics, get_chart_data

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)
        
        cards_layout = QHBoxLayout()
        
        self.card_ventas = MetricCard("Ventas (Mes)", "$0.00", "green")
        self.card_gastos = MetricCard("Gastos (Mes)", "$0.00", "red")
        self.card_balance = MetricCard("Balance Neto", "$0.00", "blue")
        self.card_stock = MetricCard("Alertas Stock Bajo", "0", "orange")
        
        cards_layout.addWidget(self.card_ventas)
        cards_layout.addWidget(self.card_gastos)
        cards_layout.addWidget(self.card_balance)
        cards_layout.addWidget(self.card_stock)
        
        main_layout.addLayout(cards_layout)
        
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_widget.setObjectName("metricCard")
        
        chart_title = QLabel("Ventas - Últimos 7 días")
        chart_title.setObjectName("metricTitle")
        chart_layout.addWidget(chart_title)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#34495E')
        self.plot_widget.setMinimumHeight(400)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getAxis('bottom').setTextPen('w')
        self.plot_widget.getAxis('left').setTextPen('w')
        
        self.chart = pg.BarGraphItem(x=[], height=[], width=0.6, brush='#3498db')
        self.plot_widget.addItem(self.chart)

        chart_layout.addWidget(self.plot_widget)
        main_layout.addWidget(chart_widget)
        
        main_layout.addStretch()
        
        self.refresh_data()

    def refresh_data(self):
        try:
            metrics = get_dashboard_metrics()
            self.card_ventas.set_value(metrics.get("ventas_mes", "$0.00"))
            self.card_gastos.set_value(metrics.get("gastos_mes", "$0.00"))
            self.card_balance.set_value(metrics.get("balance_mes", "$0.00"))
            self.card_stock.set_value(metrics.get("stock_bajo", "0"))
            
            labels, values = get_chart_data()
            
            if labels and values:
                ticks = [list(enumerate(labels))]
                self.plot_widget.getAxis('bottom').setTicks(ticks)
                self.chart.setOpts(x=list(range(len(values))), height=values)
            else:
                self.plot_widget.getAxis('bottom').setTicks(None)
                self.chart.setOpts(x=[], height=[])

        except Exception as e:
            QMessageBox.warning(self, "Error de Dashboard", f"No se pudieron cargar los datos: {e}")