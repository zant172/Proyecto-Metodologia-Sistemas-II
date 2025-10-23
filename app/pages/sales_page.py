from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Punto de Venta (POS)")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Este módulo estará disponible próximamente."))