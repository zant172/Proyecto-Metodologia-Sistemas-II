from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from .metric_card import MetricCard # <--- CORRECCIÓN AQUÍ

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        
        # 1. Título de la Página
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)
        
        # 2. Layout para las Tarjetas de Métricas
        cards_layout = QHBoxLayout()
        
        # Recreamos las tarjetas del prototipo de Canva
        card1 = MetricCard("Ventas Totales (Mes)", "$45,230", "green")
        card2 = MetricCard("Gastos Totales (Mes)", "$12,450", "red")
        card3 = MetricCard("Balance Neto", "$32,780", "blue")
        card4 = MetricCard("Alertas Stock Bajo", "8", "orange")
        
        cards_layout.addWidget(card1)
        cards_layout.addWidget(card2)
        cards_layout.addWidget(card3)
        cards_layout.addWidget(card4)
        
        main_layout.addLayout(cards_layout)
        
        # 3. Layout para el Gráfico
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_widget.setObjectName("metricCard") # Reutilizamos el estilo de tarjeta
        
        chart_title = QLabel("Ingresos vs. Egresos - Últimos 7 días")
        chart_title.setObjectName("metricTitle")
        chart_layout.addWidget(chart_title)
        
        # Creamos el gráfico (recreando el de Canva)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w') # Fondo blanco
        self.plot_widget.setMinimumHeight(400)
        
        # Datos del prototipo de Canva
        days = [1, 2, 3, 4, 5, 6, 7]
        ingresos_data = [1200, 1900, 800, 1500, 2000, 1800, 1600]
        egresos_data = [400, 600, 300, 500, 700, 600, 550]

        # Estilo de las barras
        ingresos_bar = pg.BarGraphItem(x=days, height=ingresos_data, width=0.4, brush='#3498db', name="Ingresos")
        egresos_bar = pg.BarGraphItem(x=[d + 0.4 for d in days], height=egresos_data, width=0.4, brush='#e74c3c', name="Egresos")
        
        self.plot_widget.addItem(ingresos_bar)
        self.plot_widget.addItem(egresos_bar)
        
        # Configurar ejes (simplificado)
        ax = self.plot_widget.getAxis('bottom')
        ticks = [list(zip(days, ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']))]
        ax.setTicks(ticks)

        chart_layout.addWidget(self.plot_widget)
        main_layout.addWidget(chart_widget)
        
        main_layout.addStretch() # Empuja todo hacia arriba