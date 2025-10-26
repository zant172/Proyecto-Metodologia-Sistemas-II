from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class MetricCard(QWidget):
    def __init__(self, title, value, theme_color="blue"):
        super().__init__()
        self.setMinimumHeight(120)
        self.setObjectName("metricCard")
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("metricTitle")
        
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metricValue")
        
        self.set_theme_color(theme_color)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_theme_color(self, theme_color):
        if theme_color == "green":
            self.value_label.setStyleSheet("color: #27AE60;")
        elif theme_color == "red":
            self.value_label.setStyleSheet("color: #E74C3C;")
        elif theme_color == "orange":
             self.value_label.setStyleSheet("color: #E67E22;")
        else:
             self.value_label.setStyleSheet("color: #3498db;")

    def set_value(self, value):
        self.value_label.setText(value)