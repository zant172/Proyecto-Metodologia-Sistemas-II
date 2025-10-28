import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QComboBox, QFormLayout,
                             QStackedWidget, QFrame, QApplication, QWidget)
from PyQt6.QtCore import Qt
from ..auth import create_user, mark_setup_complete, create_default_categories

class SettingsG_Windows(QDialog):
    # Asistente de configuración inicial mostrado al Super Admin la primera vez
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración Inicial - InfinityTech")
        self.setMinimumWidth(550)
        # self.setModal(True) # Hace que bloquee login hasta terminar

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        # --- Indicador de Pasos (visual) ---
        self.step_indicator_layout = QHBoxLayout()
        self.step1_indicator = QLabel(" <b>1. Negocio</b> ") # Paso actual en negrita
        self.step2_indicator = QLabel(" 2. Admin ")
        # Estilos iniciales (activo/inactivo)
        self.step1_indicator.setStyleSheet("color: #6366F1; border-bottom: 2px solid #6366F1; padding-bottom: 5px;")
        self.step2_indicator.setStyleSheet("color: #94A3B8; padding-bottom: 5px;") # Color secundario QSS
        self.step_indicator_layout.addWidget(self.step1_indicator)
        self.step_indicator_layout.addWidget(QLabel("→")) # Separador simple
        self.step_indicator_layout.addWidget(self.step2_indicator)
        self.step_indicator_layout.addStretch() # Empuja a la izquierda
        self.main_layout.addLayout(self.step_indicator_layout)
        self.main_layout.addWidget(self.create_separator()) # Línea divisoria

        # --- Contenedor de Pasos (QStackedWidget) ---
        self.stacked_widget = QStackedWidget()
        self.current_step = 0 # Guarda el índice del paso actual

        # --- PASO 1: Datos del Negocio ---
        step1_widget = QWidget() # Contenedor para el paso 1
        step1_layout = QVBoxLayout(step1_widget)
        step1_title = QLabel("Información del Negocio")
        step1_title.setObjectName("pageTitle") # Usa estilo QSS
        step1_title.setStyleSheet("font-size: 24px; margin-bottom: 10px; border-bottom: none;") # Ajustes locales
        step1_layout.addWidget(step1_title)
        step1_layout.addWidget(QLabel("Ingresa el nombre y selecciona el rubro principal de tu negocio."))
        step1_layout.addSpacing(25) # Espacio vertical

        form_layout_s1 = QFormLayout() # Layout para etiquetas y campos
        form_layout_s1.setVerticalSpacing(15)
        self.nombre_negocio_input = QLineEdit()
        self.nombre_negocio_input.setPlaceholderText("Ej: Ferretería Hernández")
        self.tipo_negocio_combo = QComboBox()
        self.tipo_negocio_combo.addItems([ # Opciones de tipo de negocio
            "Kiosko / Almacén",
            "Ferretería",
            "Tienda de Ropa",
            "Tienda de Electrónicos",
            "Otro / Mixto"
        ])
        # Añade filas al formulario (Label, Input)
        form_layout_s1.addRow("Nombre del Negocio:", self.nombre_negocio_input)
        form_layout_s1.addRow("Tipo de Negocio:", self.tipo_negocio_combo)
        step1_layout.addLayout(form_layout_s1)
        step1_layout.addStretch() # Empuja formulario hacia arriba

        # --- PASO 2: Crear Cuenta Administrador ---
        step2_widget = QWidget() # Contenedor para el paso 2
        step2_layout = QVBoxLayout(step2_widget)
        step2_title = QLabel("Crear Cuenta de Administrador")
        step2_title.setObjectName("pageTitle")
        step2_title.setStyleSheet("font-size: 24px; margin-bottom: 10px; border-bottom: none;")
        step2_layout.addWidget(step2_title)
        step2_layout.addWidget(QLabel("Crea la cuenta principal (dueño/gerente). Podrá crear más usuarios luego."))
        step2_layout.addSpacing(25)

        form_layout_s2 = QFormLayout()
        form_layout_s2.setVerticalSpacing(15)
        self.admin_username_input = QLineEdit()
        self.admin_username_input.setPlaceholderText("Ej: admin_juan")
        self.admin_fullname_input = QLineEdit()
        self.admin_fullname_input.setPlaceholderText("Ej: Juan Pérez")
        self.admin_password_input = QLineEdit()
        self.admin_password_input.setEchoMode(QLineEdit.EchoMode.Password) # Oculta contraseña
        self.admin_password_input.setPlaceholderText("Mínimo 6 caracteres")

        form_layout_s2.addRow("Nombre de Usuario:", self.admin_username_input)
        form_layout_s2.addRow("Nombre Completo:", self.admin_fullname_input)
        form_layout_s2.addRow("Contraseña:", self.admin_password_input)
        step2_layout.addLayout(form_layout_s2)
        step2_layout.addStretch()

        # Añadir los widgets de cada paso al QStackedWidget
        self.stacked_widget.addWidget(step1_widget)
        self.stacked_widget.addWidget(step2_widget)
        self.main_layout.addWidget(self.stacked_widget) # Añade el stack al layout principal
        self.main_layout.addWidget(self.create_separator()) # Otra línea divisoria

        # --- Botones de Navegación (Anterior, Siguiente, Finalizar) ---
        self.button_layout = QHBoxLayout()
        self.back_button = QPushButton("← Anterior")
        self.next_button = QPushButton("Siguiente →")
        self.finish_button = QPushButton("Finalizar Configuración")

        # Asignar objectName para que tomen estilo del QSS
        self.back_button.setObjectName("cancelButton")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor) # Usa estilo default QPushButton
        self.finish_button.setObjectName("addButton") # Estilo verde
        self.finish_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.button_layout.addWidget(self.back_button)
        self.button_layout.addStretch() # Empuja botones Siguiente/Finalizar a la derecha
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.finish_button)
        self.main_layout.addLayout(self.button_layout)

        # Conectar botones a funciones
        self.next_button.clicked.connect(self.go_to_next_step)
        self.back_button.clicked.connect(self.go_to_previous_step)
        self.finish_button.clicked.connect(self.finish_setup)

        # Mostrar el primer paso inicialmente
        self.go_to_step(0)

    def create_separator(self):
        # Crea una línea horizontal simple para separar secciones
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        # Usa el color de borde del QSS para consistencia
        line.setStyleSheet("border-top: 1px solid rgba(100, 116, 139, 0.3); margin: 15px 0;")
        return line

    def update_step_indicator(self, current_index):
        # Actualiza el estilo visual del indicador de paso (1. Negocio > 2. Admin)
        active_style = "font-weight: bold; color: #6366F1; border-bottom: 2px solid #6366F1; padding-bottom: 5px;"
        inactive_style = "color: #94A3B8; border-bottom: none; padding-bottom: 5px;"
        self.step1_indicator.setStyleSheet(active_style if current_index == 0 else inactive_style)
        self.step2_indicator.setStyleSheet(active_style if current_index == 1 else inactive_style)

    def go_to_step(self, step_index):
        # Cambia la página visible en el QStackedWidget y actualiza botones/indicador
        self.current_step = step_index
        self.stacked_widget.setCurrentIndex(step_index)
        self.update_step_indicator(step_index)
        # Habilita/Deshabilita botón "Anterior"
        self.back_button.setEnabled(step_index > 0)
        # Muestra/Oculta "Siguiente" vs "Finalizar"
        self.next_button.setVisible(step_index < self.stacked_widget.count() - 1)
        self.finish_button.setVisible(step_index == self.stacked_widget.count() - 1)

    def go_to_next_step(self):
        # Valida el paso actual y avanza si es válido
        valid = True
        if self.current_step == 0: # Validando Paso 1
            if not self.nombre_negocio_input.text().strip(): # Nombre negocio obligatorio
                QMessageBox.warning(self, "Campo Obligatorio", "Por favor, ingresa el nombre del negocio.")
                valid = False
            elif self.tipo_negocio_combo.currentIndex() < 0: # Asegurar selección (aunque raro)
                 QMessageBox.warning(self, "Campo Obligatorio", "Selecciona un tipo de negocio.")
                 valid = False

        # Si es válido y no es el último paso, avanza
        if valid and self.current_step < self.stacked_widget.count() - 1:
            self.go_to_step(self.current_step + 1)

    def go_to_previous_step(self):
        # Retrocede al paso anterior si no es el primero
        if self.current_step > 0:
            self.go_to_step(self.current_step - 1)

    def finish_setup(self):
        # Se ejecuta al presionar "Finalizar Configuración" en el último paso
        # 1. Recoger todos los datos ingresados
        nombre_negocio = self.nombre_negocio_input.text().strip()
        tipo_negocio = self.tipo_negocio_combo.currentText()
        admin_username = self.admin_username_input.text().strip()
        admin_fullname = self.admin_fullname_input.text().strip()
        admin_password = self.admin_password_input.text() # Contraseña sin strip

        # 2. Validación final de campos del Admin
        if not all([nombre_negocio, tipo_negocio, admin_username, admin_fullname, admin_password]):
            QMessageBox.warning(self, "Campos Incompletos", "Completa todos los campos para crear el administrador.")
            return
        if len(admin_password) < 6: # Validación simple de longitud de contraseña
            QMessageBox.warning(self, "Contraseña Corta", "La contraseña del administrador debe tener al menos 6 caracteres.")
            return

        # 3. Ejecutar las acciones de configuración en orden
        print("Iniciando proceso de finalización de configuración...")

        # 3a. Crear categorías por defecto (desde auth.py)
        if not create_default_categories(tipo_negocio):
             # Si falla la creación de categorías, muestra error y detiene
             QMessageBox.critical(self, "Error de Configuración", "No se pudieron crear las categorías por defecto. Revisa la conexión o contacta soporte.")
             return # No continuar

        # 3b. Crear el usuario Administrador (role_id=2 para 'Admin')
        success_admin, msg_admin = create_user(admin_username, admin_password, admin_fullname, role_id=2)
        if not success_admin:
             # Si falla la creación del Admin (ej. usuario ya existe), muestra error y detiene
             QMessageBox.critical(self, "Error al Crear Administrador", msg_admin)
             return # No continuar

        # 3c. Marcar la configuración como completada en la BD (desde auth.py)
        if not mark_setup_complete(nombre_negocio, tipo_negocio):
             # Si falla guardar el estado (raro), muestra advertencia pero continúa
             QMessageBox.warning(self, "Advertencia", "No se pudo marcar la configuración como completada en la base de datos, pero el usuario administrador fue creado.")

        # 4. Si todo salió bien (o con advertencia leve), informa y cierra el asistente
        print("✅ Configuración inicial completada.")
        QMessageBox.information(self, "Configuración Completa",
                                f"¡Configuración inicial finalizada!\nSe creó el usuario administrador: '{admin_username}'.\nPuedes cerrar esta ventana e iniciar sesión con la cuenta creada.")

        # Cierra el diálogo indicando que se completó exitosamente
        self.accept()