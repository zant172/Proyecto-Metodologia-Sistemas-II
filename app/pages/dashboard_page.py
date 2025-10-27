from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from ..dashboard_logic import get_dashboard_metrics, get_chart_data

class MetricCard(QWidget): 
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("metricCard") 
        self.setMinimumHeight(120) 
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("metricTitle") 
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metricValue") 
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 

    def set_value(self, value):
        self.value_label.setText(value)

class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Usamos facecolor='none' para que tome el fondo del QSS
        self.figure = Figure(figsize=(10, 4), facecolor='none') 
        self.canvas = FigureCanvas(self.figure)
        # Hacemos el canvas transparente también
        self.canvas.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
        self.plot_sales_chart()
    
    def plot_sales_chart(self):
        labels, values = get_chart_data()
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # Hacemos el fondo del gráfico transparente
        ax.set_facecolor('none') 

        # Ajustamos colores de ejes y ticks al estilo oscuro
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#475569') # Gris oscuro del QSS
        ax.spines['left'].set_color('#475569')
        ax.tick_params(axis='x', colors='#94A3B8') # Color de texto secundario
        ax.tick_params(axis='y', colors='#94A3B8')
        ax.yaxis.label.set_color('#94A3B8')
        ax.xaxis.label.set_color('#94A3B8')
        ax.title.set_color('#E2E8F0') # Color de texto principal
        
        if not labels or not values:
            ax.text(0.5, 0.5, 'No hay datos de ventas recientes', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=ax.transAxes, color='#94A3B8')
            self.canvas.draw()
            return

        x = np.arange(len(labels))
        
        # Usamos un color del QSS para las barras
        bars = ax.bar(x, values, width=0.6, label='Ventas', color='#6366F1') 
        
        ax.set_ylabel('Monto ($)')
        ax.set_title('Ventas - Últimos 7 días')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        legend = ax.legend()
        plt.setp(legend.get_texts(), color='#E2E8F0') # Texto principal
        # Hacemos el fondo de la leyenda transparente
        legend.get_frame().set_facecolor('none')
        legend.get_frame().set_edgecolor('none')
        ax.grid(True, alpha=0.1, color='#475569') # Rejilla sutil
        
        # Ajuste final para evitar cortes
        self.figure.tight_layout()
        self.canvas.draw()

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle") 
        subtitle = QLabel("Resumen general del negocio")
        # El QSS general se encarga del color y fuente de subtítulos
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20) # Añadimos espacio entre tarjetas
        
        self.card_ventas = MetricCard("Ventas Totales (Mes)", "$0.00")
        self.card_gastos = MetricCard("Gastos Totales (Mes)", "$0.00")
        self.card_balance = MetricCard("Balance Neto", "$0.00")
        self.card_stock = MetricCard("Alertas Stock Bajo", "0")
        
        metrics_layout.addWidget(self.card_ventas)
        metrics_layout.addWidget(self.card_gastos)
        metrics_layout.addWidget(self.card_balance)
        metrics_layout.addWidget(self.card_stock)
        
        layout.addLayout(metrics_layout)
        
        # Contenedor para el gráfico con el estilo de tarjeta
        chart_container = QWidget() 
        chart_container.setObjectName("metricCard") 
        chart_layout = QVBoxLayout(chart_container)
        
        chart_title = QLabel("Ventas - Últimos 7 días")
        chart_title.setObjectName("metricTitle")
        
        self.chart_widget = ChartWidget()
        
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.chart_widget)
        
        layout.addWidget(chart_container)
        layout.addStretch() # Empuja todo hacia arriba
        
    def refresh_data(self):
        try:
            metrics = get_dashboard_metrics()
            self.card_ventas.set_value(metrics.get("ventas_mes", "$0.00"))
            self.card_gastos.set_value(metrics.get("gastos_mes", "$0.00"))
            self.card_balance.set_value(metrics.get("balance_mes", "$0.00"))
            self.card_stock.set_value(metrics.get("stock_bajo", "0"))
            
            # Aplicamos colores específicos del QSS a los valores
            self.card_gastos.value_label.setStyleSheet("color: #EF4444;") # Rojo
            self.card_stock.value_label.setStyleSheet("color: #F59E0B;") # Naranja
            self.card_ventas.value_label.setStyleSheet("color: #10B981;") # Verde
            # El azul/violeta para balance puede ser el color por defecto
            self.card_balance.value_label.setStyleSheet("color: #6366F1;") 

            # Refrescamos el gráfico
            self.chart_widget.plot_sales_chart()

        except Exception as e:
            # Mostramos el error en una QMessageBox estilizada por QSS
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Error de Dashboard")
            msg_box.setText(f"No se pudieron cargar los datos: {e}")
            msg_box.exec()