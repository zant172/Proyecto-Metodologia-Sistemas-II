from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox, QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt
from ..dashboard_logic import create_metodo_pago, update_metodo_pago

class MetodoPagoFormDialog(QDialog):
    def __init__(self, metodo_id=None, metodo_data=None, on_success=None, parent=None):
        super().__init__(parent)
        self.metodo_id = metodo_id
        self.metodo_data = metodo_data
        self.on_success = on_success

        self.setWindowTitle(f"{'Editar' if metodo_id else 'Agregar'} Método de Pago")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(20, 20, 20, 20)
        form_layout = QFormLayout(); form_layout.setVerticalSpacing(15); form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.nombre_input = QLineEdit()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(['Efectivo', 'Tarjeta', 'Digital', 'Otros'])
        self.activo_check = QCheckBox("Activo")
        self.activo_check.setChecked(True) # Activo por defecto

        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Tipo:", self.tipo_combo)
        form_layout.addRow("Estado:", self.activo_check)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar"); self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button = QPushButton("Cancelar"); self.cancel_button.setObjectName("cancelButton"); self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addStretch(); buttons_layout.addWidget(self.cancel_button); buttons_layout.addWidget(self.save_button)
        main_layout.addLayout(buttons_layout)

        if self.metodo_id and self.metodo_data:
            self.nombre_input.setText(self.metodo_data.Nombre)
            self.tipo_combo.setCurrentText(self.metodo_data.TipoMetodo or 'Otros')
            self.activo_check.setChecked(self.metodo_data.Activo)

        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def handle_save(self):
        nombre = self.nombre_input.text().strip()
        tipo = self.tipo_combo.currentText()
        activo = self.activo_check.isChecked()

        if not nombre:
            QMessageBox.warning(self, "Dato incompleto", "El nombre es obligatorio."); return

        try:
            if self.metodo_id:
                success, message = update_metodo_pago(self.metodo_id, nombre, tipo, activo)
            else:
                success, message = create_metodo_pago(nombre, tipo)
            
            msg = QMessageBox(self)
            if success:
                msg.setIcon(QMessageBox.Icon.Information); msg.setWindowTitle("Éxito"); msg.setText(message); msg.exec()
                if self.on_success: self.on_success()
                self.accept()
            else:
                msg.setIcon(QMessageBox.Icon.Critical); msg.setWindowTitle("Error"); msg.setText(message); msg.exec()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")