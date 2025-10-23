from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Reportes Financieros")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Este módulo estará disponible próximamente."))