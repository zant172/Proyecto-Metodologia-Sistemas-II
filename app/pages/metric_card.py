from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class MetricCard(QWidget):
    def __init__(self, title, value, theme_color="blue"):
        super().__init__(); self.setMinimumHeight(120); self.setObjectName("metricCard")
        layout = QVBoxLayout(self)
        self.title_label = QLabel(title); self.title_label.setObjectName("metricTitle")
        self.value_label = QLabel(value); self.value_label.setObjectName("metricValue")
        self.set_theme_color(theme_color)
        layout.addWidget(self.title_label); layout.addWidget(self.value_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_theme_color(self, color):
        style = {"green": "#27AE60", "red": "#E74C3C", "orange": "#E67E22"}.get(color, "#3498db")
        self.value_label.setStyleSheet(f"color: {style};")

    def set_value(self, value): self.value_label.setText(value)