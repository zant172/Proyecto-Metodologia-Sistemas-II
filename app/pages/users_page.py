from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from functools import partial
# Importa las funciones necesarias de auth.py
from ..auth import get_all_users, get_user_by_id, delete_user
# Importa el diálogo de formulario de usuario
from .user_form_dialog import UserFormDialog

class UserTableWidget(QTableWidget):
    # Esta clase se encarga de mostrar la tabla de usuarios
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget # Referencia a UsersWidget
        self.setup_table()

    def setup_table(self):
        # Configura las columnas y el estilo base de la tabla
        self.setColumnCount(5) # ID, Usuario, Nombre, Rol, Acciones
        self.setHorizontalHeaderLabels(['ID', 'Nombre de Usuario', 'Nombre Completo', 'Rol', 'Acciones'])

        # Configuración del Header para que coincida con el QSS
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents) # Ajusta ID, Usuario, Rol
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Nombre Completo toma espacio
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch) # Acciones toma espacio

        # Configuraciones generales de la tabla
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # Seleccionar filas completas
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # No editable directamente
        self.setColumnHidden(0, True) # Ocultamos la columna ID
        self.verticalHeader().setVisible(False) # Ocultamos header vertical
        self.setShowGrid(False) # El QSS maneja los bordes

    def load_users(self):
        # Carga los usuarios desde la base de datos (auth.py)
        users, error = get_all_users()
        if error:
            # Muestra error si falla la carga
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error de Base de Datos")
            msg_box.setText(f"No se pudieron cargar los usuarios:\n{error}")
            msg_box.exec()
            self.setRowCount(0) # Limpia la tabla si hay error
            return

        self.setRowCount(len(users)) # Ajusta número de filas

        # Llena la tabla fila por fila
        for row, user in enumerate(users):
            user_id = user[0]

            # Añade los datos a las celdas
            self.setItem(row, 0, QTableWidgetItem(str(user_id)))
            self.setItem(row, 1, QTableWidgetItem(user[1])) # NombreUsuario
            self.setItem(row, 2, QTableWidgetItem(user[2])) # NombreCompleto
            self.setItem(row, 3, QTableWidgetItem(user[3])) # NombreRol

            # --- Columna de Acciones ---
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes internos
            actions_layout.setSpacing(10) # Espacio entre botones

            # Botón Editar
            edit_btn = QPushButton("Editar")
            edit_btn.setObjectName("editButton") # ID para QSS
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Conecta el clic a la función open_edit_dialog de UsersWidget
            edit_btn.clicked.connect(partial(self.parent_widget.open_edit_dialog, user_id))

            # Botón Eliminar
            delete_btn = QPushButton("Eliminar")
            delete_btn.setObjectName("deleteButton") # ID para QSS
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Conecta el clic a la función handle_delete de UsersWidget
            delete_btn.clicked.connect(partial(self.parent_widget.handle_delete, user_id))

            # Añade botones al layout de acciones
            actions_layout.addStretch() # Empuja a la derecha
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch() # Centra si hay espacio

            # Pone el widget con los botones en la celda de acciones
            self.setCellWidget(row, 4, actions_widget)

class UsersWidget(QWidget):
    # Esta es la clase principal para la pestaña de Gestión de Usuarios
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Configura el layout principal de la página
        layout = QVBoxLayout(self)

        # --- Cabecera ---
        header_layout = QVBoxLayout()
        title = QLabel("Gestión de Usuarios")
        title.setObjectName("pageTitle") # ID para QSS
        subtitle = QLabel("Administra las cuentas del personal")
        # El QSS general se encarga del estilo del subtítulo

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)

        # --- Controles (Búsqueda y Agregar) ---
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 20) # Espaciado
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar usuario...")
        # El QSS general se encarga del estilo del QLineEdit

        add_btn = QPushButton("Agregar Usuario")
        add_btn.setObjectName("addButton") # ID para QSS (botón verde)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_dialog) # Conecta a la función para abrir el diálogo

        controls_layout.addWidget(search_input, 1) # Campo de búsqueda ocupa más espacio
        controls_layout.addWidget(add_btn)
        layout.addLayout(controls_layout)

        # --- Tabla de Usuarios ---
        self.users_table = UserTableWidget(self) # Crea la instancia de la tabla
        layout.addWidget(self.users_table)

    def refresh_data(self):
        # Este método es crucial. MainWindow lo llama cuando se cambia a esta pestaña.
        # Le dice a la tabla que vuelva a cargar los datos desde la BD.
        print("Refrescando datos de Usuarios...") # Mensaje de depuración
        self.users_table.load_users()

    def open_add_dialog(self):
        # Abre el diálogo para agregar un nuevo usuario
        # Pasa self.refresh_data como callback para que la tabla se actualice si se guarda con éxito
        dialog = UserFormDialog(on_success=self.refresh_data, parent=self)
        dialog.exec() # Muestra el diálogo

    def open_edit_dialog(self, user_id):
        # Abre el diálogo para editar un usuario existente
        # 1. Busca los datos del usuario por su ID usando auth.py
        user_data, error = get_user_by_id(user_id)
        if error or not user_data:
            # Muestra error si no se pueden cargar los datos
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"No se pudieron cargar los datos del usuario: {error}")
            msg_box.exec()
            return

        # 2. Abre el UserFormDialog, pasando el user_id y los user_data
        dialog = UserFormDialog(user_id=user_id, user_data=user_data, on_success=self.refresh_data, parent=self)
        dialog.exec()

    def handle_delete(self, user_id):
        # Maneja el clic en el botón "Eliminar" de la tabla
        # 1. Muestra un diálogo de confirmación
        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       "¿Está seguro de que desea eliminar a este usuario?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # 2. Si el usuario confirma...
        if confirm == QMessageBox.StandardButton.Yes:
            # Llama a la función delete_user de auth.py (que hace soft delete)
            success, message = delete_user(user_id)
            # Muestra un mensaje con el resultado
            msg_box = QMessageBox(self)
            if success:
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("Éxito")
            else:
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("Error")
            msg_box.setText(message)
            msg_box.exec()
            # 3. Si se eliminó correctamente, refresca la tabla
            if success:
                self.refresh_data()