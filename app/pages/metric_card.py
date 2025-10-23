from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class MetricCard(QWidget):
    """
    Un widget de "tarjeta" para mostrar una métrica clave en el dashboard.
    """
    def __init__(self, title, value, theme_color="blue"):
        super().__init__()
        self.setMinimumHeight(120)
        self.setObjectName("metricCard")
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("metricTitle")
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metricValue")
        
        # Aplicar color basado en el tema
        if theme_color == "green":
            self.value_label.setStyleSheet("color: #27AE60;")
        elif theme_color == "red":
            self.value_label.setStyleSheet("color: #E74C3C;")
        elif theme_color == "orange":
             self.value_label.setStyleSheet("color: #E67E22;")
        else:
             self.value_label.setStyleSheet("color: #3498db;") # default blue
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)