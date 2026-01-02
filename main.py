"""
Sistema de Gestión de Ventas SJG - Versión Completa con Flet
Toda la lógica del sistema adaptada a Flet Framework
"""
import flet as ft
import json
import os
from app.database import set_connection_parameters, initialize_database_schema, test_connection, drop_database
from app.auth import (login_user, get_all_users, create_user, update_user, delete_user, get_all_roles, 
                      ensure_superadmin_exists, is_initial_setup_complete, mark_setup_complete, 
                      create_default_categories)
from app.dashboard_logic import (get_dashboard_metrics, get_employee_metrics, get_chart_data,
                                 perform_cierre_caja, check_cierre_realizado_hoy, 
                                 get_resumen_dia_actual, get_historial_cierres)
from app.products import (get_all_products, create_product, update_product, delete_product, 
                          get_all_categories, search_products, get_product_by_id)
from app.caja_logic import (get_caja_activa, abrir_caja, pausar_caja, reanudar_caja, 
                            cerrar_caja, get_resumen_caja_activa, get_historial_cajas,
                            get_ventas_de_caja, get_detalle_venta)
from app.gastos import get_all_gastos, create_gasto, update_gasto, delete_gasto
from app.metodos_pago import get_all_metodos_pago, create_metodo_pago, update_metodo_pago, delete_metodo_pago
from app.reportes import get_ventas_por_fecha, get_gastos_por_fecha, get_resumen_financiero, get_ventas_por_metodo_pago
from app.sales_logic import process_sale
from datetime import datetime, timedelta

# Archivo de configuración de conexión
CONNECTION_FILE = 'connection_data.json'

def load_connection_params():
    """Carga parámetros de conexión desde archivo JSON"""
    if os.path.exists(CONNECTION_FILE):
        try:
            with open(CONNECTION_FILE, 'r', encoding='utf-8') as f:
                params = json.load(f)
                if all(k in params for k in ['server', 'database']):
                    print(f"✅ Configuración de conexión cargada desde {CONNECTION_FILE}")
                    return params
                else:
                    print(f"⚠️ Archivo {CONNECTION_FILE} inválido (faltan claves).")
                    return None
        except Exception as e:
            print(f"❌ Error al leer {CONNECTION_FILE}: {e}")
            return None
    else:
        print(f"ℹ️  No se encontró {CONNECTION_FILE}. Usando configuración por defecto.")
        return None

def save_connection_params(details):
    """Guarda parámetros de conexión en archivo JSON"""
    try:
        with open(CONNECTION_FILE, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=4)
        print(f"✅ Configuración de conexión guardada en {CONNECTION_FILE}")
    except Exception as e:
        print(f"❌ Error al guardar {CONNECTION_FILE}: {e}")

def initialize_system():
    """Inicializa la base de datos y crea el superadmin si no existe"""
    connection_ok = False
    connection_details = None
    
    # Intentar cargar configuración guardada
    saved_params = load_connection_params()
    if saved_params:
        set_connection_parameters(**saved_params)
        success, msg = test_connection(saved_params['server'], 'master',
                                       saved_params.get('username'), 
                                       saved_params.get('password'),
                                       saved_params.get('trusted', True))
        if success:
            print("✅ Conexión automática exitosa con parámetros guardados.")
            connection_ok = True
            connection_details = saved_params
        else:
            print(f"⚠️ Falló conexión automática: {msg}")
            # Intentar con valores por defecto
            default_params = {
                'server': 'localhost\\SQLEXPRESS',
                'database': 'sistemgestionvntsjg',
                'username': None,
                'password': None,
                'trusted': True
            }
            set_connection_parameters(**default_params)
            success, msg = test_connection(default_params['server'], 'master', None, None, True)
            if success:
                print("✅ Conexión exitosa con parámetros por defecto.")
                connection_ok = True
                connection_details = default_params
                save_connection_params(default_params)
    else:
        # Usar configuración por defecto
        default_params = {
            'server': 'localhost\\SQLEXPRESS',
            'database': 'sistemgestionvntsjg',
            'username': None,
            'password': None,
            'trusted': True
        }
        set_connection_parameters(**default_params)
        success, msg = test_connection(default_params['server'], 'master', None, None, True)
        if success:
            print("✅ Conexión exitosa con parámetros por defecto.")
            connection_ok = True
            connection_details = default_params
            save_connection_params(default_params)
        else:
            print(f"❌ No se pudo conectar a la base de datos: {msg}")
            return False
    
    # Si tenemos conexión, inicializar schema y superadmin
    if connection_ok:
        if not initialize_database_schema():
            print("❌ Error al inicializar el esquema de la base de datos.")
            return False
        
        # ensure_superadmin_exists() no retorna valor, solo imprime mensajes
        ensure_superadmin_exists()
        
        print("✅ Sistema inicializado correctamente.")
        return True
    
    return False


class SistemaGestionApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sistema de Gestión de Ventas SJG"
        self.page.window_width = 1600
        self.page.window_height = 1000
        self.page.window_min_width = 1200
        self.page.window_min_height = 700
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = "#FAFBFC"
        
        self.user_data = None
        self.current_view = None
        self.cart_items = []
        self.setup_step = 0
        self.setup_data = {}
        self.config = None  # Configuración del sistema
        
        # Paleta de colores mejorada con gradientes
        self.colors = {
            "primary": "#7C9DD6",          # Azul pastel suave
            "primary_dark": "#6889C0",     # Azul pastel medio
            "primary_light": "#B5D0EE",    # Azul pastel muy claro
            "success": "#81C995",          # Verde pastel
            "success_light": "#D4F1DD",    # Verde muy claro
            "warning": "#F5C461",          # Amarillo pastel cálido
            "warning_light": "#FFF4DC",    # Amarillo muy claro
            "danger": "#F38B8B",           # Rojo/coral pastel
            "danger_light": "#FFE5E5",     # Rojo muy claro
            "info": "#80C3E3",             # Cyan pastel
            "info_light": "#E0F3FB",       # Cyan muy claro
            "bg": "#F8F9FB",               # Gris azulado muy claro
            "bg_dark": "#EDF0F5",          # Gris azulado claro
            "card": "#FFFFFF",             # Blanco puro
            "card_hover": "#FCFDFE",       # Blanco con tinte azul
            "text_primary": "#2D3748",     # Gris oscuro
            "text_secondary": "#4A5568",   # Gris medio
            "text_muted": "#A0AEC0",       # Gris claro
            "border": "#E2E8F0",           # Borde gris azulado
            "border_light": "#F1F5F9",     # Borde muy claro
            "shadow": "#7C9DD615",         # Sombra azul pastel
        }
        
        # Verificar si es primera vez (setup pendiente)
        if not is_initial_setup_complete():
            print("ℹ️  Setup inicial pendiente")
            self.show_setup_wizard()
        else:
            print("✅ Setup completo, mostrando login")
            self.show_login()
    
    def show_setup_wizard(self):
        """Asistente de configuración inicial de 2 pasos: Negocio + Admin"""
        self.page.controls.clear()
        
        # Indicadores de paso
        step1_style = {"color": self.colors["primary"], "weight": ft.FontWeight.BOLD, "size": 16} if self.setup_step == 0 else {"color": self.colors["text_secondary"], "size": 16}
        step2_style = {"color": self.colors["primary"], "weight": ft.FontWeight.BOLD, "size": 16} if self.setup_step == 1 else {"color": self.colors["text_secondary"], "size": 16}
        
        indicator = ft.Row([
            ft.Text("1. Negocio", **step1_style),
            ft.Text("→", size=16),
            ft.Text("2. Administrador", **step2_style),
        ], spacing=10)
        
        # Contenedor del paso actual
        if self.setup_step == 0:
            step_content = self.build_step1_setup()
        else:
            step_content = self.build_step2_setup()
        
        # Botones de navegación
        back_btn = ft.OutlinedButton(
            "← Anterior",
            on_click=lambda _: self.go_to_setup_step(0),
            disabled=self.setup_step == 0,
            width=150
        )
        
        next_btn = ft.ElevatedButton(
            "Siguiente →",
            on_click=lambda _: self.validate_and_next_step(),
            bgcolor=self.colors["primary"],
            color="white",
            width=150,
            visible=self.setup_step == 0
        )
        
        finish_btn = ft.ElevatedButton(
            "Finalizar Configuración",
            on_click=lambda _: self.finish_setup_wizard(),
            bgcolor=self.colors["success"],
            color="white",
            width=200,
            visible=self.setup_step == 1
        )
        
        buttons_row = ft.Row([
            back_btn,
            ft.Container(expand=True),
            next_btn,
            finish_btn,
        ])
        
        self.page.add(
            ft.Container(
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(height=20),
                        ft.Row([
                            ft.Icon(ft.Icons.SETTINGS, size=40, color=self.colors["primary"]),
                            ft.Text("Configuración Inicial", size=28, weight=ft.FontWeight.BOLD),
                        ], spacing=15),
                        ft.Container(height=10),
                        indicator,
                        ft.Divider(height=30, color=self.colors["border"]),
                        step_content,
                        ft.Divider(height=30, color=self.colors["border"]),
                        buttons_row,
                        ft.Container(height=20),
                    ]),
                    bgcolor=self.colors["card"],
                    padding=40,
                    border_radius=16,
                    border=ft.border.all(1, self.colors["border"]),
                    width=650,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="#00000010")
                ),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=self.colors["bg"]
            )
        )
        self.page.update()
    
    def build_step1_setup(self):
        """Paso 1: Información del negocio"""
        self.nombre_negocio_field = ft.TextField(
            label="Nombre del Negocio *",
            width=500,
            hint_text="Ej: Ferretería Hernández",
            autofocus=True
        )
        
        self.tipo_negocio_dropdown = ft.Dropdown(
            label="Tipo de Negocio *",
            width=500,
            hint_text="Seleccionar...",
            options=[
                ft.dropdown.Option("Kiosko / Almacén"),
                ft.dropdown.Option("Ferretería"),
                ft.dropdown.Option("Tienda de Ropa"),
                ft.dropdown.Option("Tienda de Electrónicos"),
                ft.dropdown.Option("Otro / Mixto"),
            ]
        )
        
        self.usar_codigos_barra_checkbox = ft.Checkbox(
            label="Usar códigos de barra (escáner)",
            value=False
        )
        
        # Restaurar valores si vuelve del paso 2
        if 'nombre_negocio' in self.setup_data:
            self.nombre_negocio_field.value = self.setup_data['nombre_negocio']
            self.tipo_negocio_dropdown.value = self.setup_data['tipo_negocio']
            self.usar_codigos_barra_checkbox.value = self.setup_data.get('usar_codigos_barra', False)
        
        return ft.Column([
            ft.Text("Información del Negocio", size=22, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text("Ingresa el nombre y selecciona el rubro principal de tu negocio.",
                   color=self.colors["text_secondary"]),
            ft.Container(height=25),
            self.nombre_negocio_field,
            ft.Container(height=15),
            self.tipo_negocio_dropdown,
            ft.Container(height=20),
            self.usar_codigos_barra_checkbox,
            ft.Text("Si activas esta opción, podrás registrar códigos de barra en tus productos y usar escáner en el punto de venta.",
                   size=12, color=self.colors["text_secondary"], italic=True),
            ft.Container(height=10),
            ft.Text("Las categorías de productos se crearán automáticamente según el tipo seleccionado.",
                   size=12, color=self.colors["text_secondary"], italic=True),
        ], spacing=0)
    
    def build_step2_setup(self):
        """Paso 2: Crear cuenta administrador"""
        self.admin_username_field = ft.TextField(
            label="Nombre de Usuario *",
            width=500,
            hint_text="Ej: admin_juan",
            autofocus=True
        )
        
        self.admin_fullname_field = ft.TextField(
            label="Nombre Completo *",
            width=500,
            hint_text="Ej: Juan Pérez"
        )
        
        self.admin_password_field = ft.TextField(
            label="Contraseña *",
            width=500,
            password=True,
            can_reveal_password=True,
            hint_text="Mínimo 6 caracteres"
        )
        
        # Restaurar valores si ya los ingresó
        if 'admin_username' in self.setup_data:
            self.admin_username_field.value = self.setup_data['admin_username']
            self.admin_fullname_field.value = self.setup_data['admin_fullname']
        
        return ft.Column([
            ft.Text("Crear Cuenta de Administrador", size=22, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text("Crea la cuenta principal (dueño/gerente). Podrás crear más usuarios después.",
                   color=self.colors["text_secondary"]),
            ft.Container(height=25),
            self.admin_username_field,
            ft.Container(height=15),
            self.admin_fullname_field,
            ft.Container(height=15),
            self.admin_password_field,
            ft.Container(height=10),
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=self.colors["info"], size=16),
                ft.Text("Este usuario tendrá permisos completos sobre el sistema.",
                       size=12, color=self.colors["text_secondary"], italic=True),
            ], spacing=8),
        ], spacing=0)
    
    def go_to_setup_step(self, step):
        """Cambiar de paso en el asistente"""
        self.setup_step = step
        self.show_setup_wizard()
    
    def validate_and_next_step(self):
        """Validar paso 1 y avanzar a paso 2"""
        nombre = self.nombre_negocio_field.value.strip() if self.nombre_negocio_field.value else ""
        tipo = self.tipo_negocio_dropdown.value
        usar_codigos = self.usar_codigos_barra_checkbox.value
        
        if not nombre:
            self.show_snackbar("⚠️ Por favor, ingresa el nombre del negocio", error=True)
            return
        
        if not tipo:
            self.show_snackbar("⚠️ Selecciona un tipo de negocio", error=True)
            return
        
        # Guardar datos del paso 1
        self.setup_data['nombre_negocio'] = nombre
        self.setup_data['tipo_negocio'] = tipo
        self.setup_data['usar_codigos_barra'] = usar_codigos
        
        # Avanzar al paso 2
        self.go_to_setup_step(1)
    
    def finish_setup_wizard(self):
        """Finalizar asistente: crear admin, categorías y marcar setup completo"""
        username = self.admin_username_field.value.strip() if self.admin_username_field.value else ""
        fullname = self.admin_fullname_field.value.strip() if self.admin_fullname_field.value else ""
        password = self.admin_password_field.value if self.admin_password_field.value else ""
        
        # Validaciones finales
        if not username or not fullname or not password:
            self.show_snackbar("⚠️ Completa todos los campos para crear el administrador", error=True)
            return
        
        if len(password) < 6:
            self.show_snackbar("⚠️ La contraseña debe tener al menos 6 caracteres", error=True)
            return
        
        # Guardar datos del paso 2
        self.setup_data['admin_username'] = username
        self.setup_data['admin_fullname'] = fullname
        
        print("🔧 Iniciando proceso de configuración final...")
        
        # 1. Crear categorías por defecto
        print(f"📦 Creando categorías para: {self.setup_data['tipo_negocio']}")
        if not create_default_categories(self.setup_data['tipo_negocio']):
            self.show_snackbar("❌ Error al crear categorías. Revisa la conexión", error=True)
            return
        
        # 2. Crear usuario administrador (role_id=2 para Admin)
        print(f"👤 Creando usuario administrador: {username}")
        success_admin, msg_admin = create_user(username, password, fullname, role_id=2)
        if not success_admin:
            self.show_snackbar(f"❌ {msg_admin}", error=True)
            return
        
        # 3. Marcar configuración como completada
        print("✅ Marcando configuración como completada")
        if not mark_setup_complete(self.setup_data['nombre_negocio'], self.setup_data['tipo_negocio'], self.setup_data.get('usar_codigos_barra', False)):
            self.show_snackbar("⚠️ No se pudo guardar la configuración, pero el usuario fue creado", error=True)
        
        # 4. Éxito - mostrar mensaje y redirigir a login
        print("✅ Configuración inicial completada exitosamente")
        self.show_snackbar(f"✅ ¡Configuración completa! Usuario '{username}' creado correctamente")
        
        # Esperar 2 segundos y mostrar login
        import time
        time.sleep(2)
        self.show_login()

    def show_custom_dialog(self, title, content, actions):
        """Mostrar diálogo personalizado con overlay"""
        def close_dialog(e):
            self.dialog_overlay.visible = False
            self.page.update()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=close_dialog,
                        icon_size=20
                    )
                ]),
                ft.Divider(),
                content,
                ft.Divider(),
                ft.Row(actions, alignment=ft.MainAxisAlignment.END, spacing=10),
            ], tight=True),
            width=500,
            bgcolor=self.colors["card"],
            border_radius=12,
            padding=20,
            border=ft.border.all(2, self.colors["border"]),
            shadow=ft.BoxShadow(
                spread_radius=5,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
            )
        )
        
        self.dialog_overlay = ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
            visible=True
        )
        
        self.page.overlay.append(self.dialog_overlay)
        self.page.update()
        return self.dialog_overlay

    def show_login(self):
        self.page.controls.clear()
        
        # Contenedor para mensajes de error
        self.login_error_message = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=self.colors["danger"], size=20),
                ft.Text("", size=14, color=self.colors["danger"], weight=ft.FontWeight.W_500),
            ], spacing=10),
            visible=False,
            bgcolor=self.colors["danger_light"],
            border=ft.border.all(1, self.colors["danger"]),
            border_radius=10,
            padding=15,
            width=420,
        )
        
        self.username_field = ft.TextField(
            label="Usuario", 
            prefix_icon=ft.Icons.PERSON_ROUNDED,
            width=420, 
            height=62,
            autofocus=True, 
            border_radius=14,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            bgcolor=self.colors["bg"],
            text_size=15,
            on_submit=lambda _: self.handle_login()
        )
        
        self.password_field = ft.TextField(
            label="Contraseña", 
            prefix_icon=ft.Icons.LOCK_ROUNDED,
            password=True, 
            can_reveal_password=True, 
            width=420,
            height=62,
            border_radius=14,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            bgcolor=self.colors["bg"],
            text_size=15,
            on_submit=lambda _: self.handle_login()
        )
        
        login_btn = ft.ElevatedButton(
            "Iniciar Sesión", 
            icon=ft.Icons.LOGIN_ROUNDED,
            on_click=lambda _: self.handle_login(),
            bgcolor=self.colors["primary"], 
            color="white", 
            width=420,
            height=58,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                shadow_color=self.colors["primary"] + "40",
                elevation=2,
            )
        )
        
        # Panel izquierdo con gradiente
        left_panel = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.STORE_ROUNDED, size=80, color="white"),
                ft.Container(height=25),
                ft.Text("Sistema de", size=20, color="white", weight=ft.FontWeight.W_300),
                ft.Text("Gestión de Ventas", size=36, color="white", weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                ft.Text("SJG Solutions", size=18, color="white70"),
                ft.Container(height=50),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.INVENTORY_2_ROUNDED, color="white", size=20),
                            ft.Text("Control de inventario", color="white", size=14)
                        ], spacing=10),
                        ft.Container(height=12),
                        ft.Row([
                            ft.Icon(ft.Icons.POINT_OF_SALE_ROUNDED, color="white", size=20),
                            ft.Text("Punto de venta", color="white", size=14)
                        ], spacing=10),
                        ft.Container(height=12),
                        ft.Row([
                            ft.Icon(ft.Icons.ASSESSMENT_ROUNDED, color="white", size=20),
                            ft.Text("Reportes y análisis", color="white", size=14)
                        ], spacing=10),
                    ]),
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[self.colors["primary"], self.colors["primary_dark"]],
            ),
            expand=1,
            padding=50,
        )
        
        # Panel derecho con formulario
        right_panel = ft.Container(
            content=ft.Column([
                ft.Text("Bienvenido", size=32, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                ft.Text("Inicia sesión para continuar", size=15, color=self.colors["text_muted"]),
                ft.Container(height=35),
                self.login_error_message,
                ft.Container(height=10),
                self.username_field, 
                ft.Container(height=18),
                self.password_field, 
                ft.Container(height=30),
                login_btn,
                ft.Container(height=25),
                ft.Text("v1.0 - Sistema de Gestión de Ventas SJG", size=12, color=self.colors["text_muted"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=self.colors["card"], 
            expand=1,
            padding=60,
        )
        
        self.page.add(
            ft.Row([
                left_panel,
                right_panel,
            ], spacing=0, expand=True)
        )
        self.page.update()

    def handle_login(self):
        # Ocultar mensaje de error previo
        if hasattr(self, 'login_error_message'):
            self.login_error_message.visible = False
            self.page.update()
        
        if not self.username_field.value or not self.password_field.value:
            self.show_login_error("Complete todos los campos")
            return
        
        result = login_user(self.username_field.value, self.password_field.value)
        
        if result and result.get('success'):
            self.user_data = result['user_data']
            # Cargar configuración del sistema
            from app.auth import get_configuracion
            self.config = get_configuracion()
            self.show_main_app()
        else:
            msg = result.get('message', 'Error de autenticación') if result else 'Error de conexión'
            self.show_login_error(msg)
    
    def show_login_error(self, message):
        """Muestra un mensaje de error en el formulario de login"""
        if hasattr(self, 'login_error_message'):
            # Actualizar el texto del error
            self.login_error_message.content.controls[1].value = message
            self.login_error_message.visible = True
            
            # Resaltar campos con error
            self.username_field.border_color = self.colors["danger"]
            self.password_field.border_color = self.colors["danger"]
            
            # Limpiar contraseña por seguridad
            self.password_field.value = ""
            
            self.page.update()
            
            # Restaurar colores después de 2 segundos
            import threading
            def restore_colors():
                import time
                time.sleep(2)
                if hasattr(self, 'username_field'):
                    self.username_field.border_color = self.colors["border"]
                    self.password_field.border_color = self.colors["border"]
                    self.page.update()
            threading.Thread(target=restore_colors, daemon=True).start()

    def show_main_app(self):
        try:
            self.page.controls.clear()
            
            # Menú desplegable del usuario
            def toggle_user_menu(e):
                user_menu.visible = not user_menu.visible
                self.page.update()
            
            def close_user_menu():
                user_menu.visible = False
                self.page.update()
            
            user_menu = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON_ROUNDED, color=self.colors["text_secondary"], size=20),
                                ft.Container(width=10),
                                ft.Column([
                                    ft.Text(self.user_data.get('nombre_completo', 'Usuario'), 
                                           size=14, weight=ft.FontWeight.W_500, color=self.colors["text_primary"]),
                                    ft.Text(f"Rol: {self.user_data.get('rol', 'N/A')}", 
                                           size=12, color=self.colors["text_muted"]),
                                ], spacing=2),
                            ]),
                            ft.Divider(height=1, color=self.colors["border"]),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=self.colors["danger"], size=18),
                                    ft.Container(width=10),
                                    ft.Text("Cerrar Sesión", size=13, color=self.colors["danger"]),
                                ]),
                                padding=10,
                                border_radius=8,
                                ink=True,
                                on_click=lambda _: (close_user_menu(), self.logout()),
                                on_hover=lambda e: setattr(e.control, 'bgcolor', self.colors["danger_light"] if e.data == "true" else None) or self.page.update(),
                            ),
                        ], spacing=5),
                        padding=15,
                        bgcolor=self.colors["card"],
                        border_radius=12,
                        border=ft.border.all(1, self.colors["border"]),
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color="#00000020", offset=ft.Offset(0, 5)),
                        width=250,
                    ),
                ]),
                visible=False,
                top=70,
                right=35,
            )
            
            app_bar = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.STORE_ROUNDED, color="white", size=32),
                            ft.Container(width=15),
                            ft.Column([
                                ft.Text("Sistema de Gestión de Ventas", size=20, weight=ft.FontWeight.BOLD, color="white"),
                                ft.Text("SJG Solutions", size=11, color="#FFFFFF99"),
                            ], spacing=0),
                        ]),
                        # Solo desarrolladores pueden hacer clic en el logo para resetear
                        on_click=self.logo_click_handler if self.user_data.get('rol') == 'Dev' else None,
                        ink=True if self.user_data.get('rol') == 'Dev' else False,
                        tooltip="🔴 RESET SISTEMA (Solo Dev)" if self.user_data.get('rol') == 'Dev' else None,
                        border_radius=8,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON_ROUNDED, color="#6B7688", size=18),
                            ft.Container(width=8),
                            ft.Text(f"{self.user_data.get('nombre_completo', 'Usuario')}", color="#3E4A59", size=15, weight=ft.FontWeight.W_500),
                            ft.Container(width=10),
                            ft.Icon(ft.Icons.ARROW_DROP_DOWN_ROUNDED, color="#6B7688", size=20),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        bgcolor="#E8ECF1",
                        border_radius=10,
                        ink=True,
                        on_click=toggle_user_menu,
                        tooltip="Menú de usuario",
                    ),
                ]),
                bgcolor="#7C9DD6", 
                padding=ft.padding.symmetric(horizontal=35, vertical=18),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#00000015", offset=ft.Offset(0, 2))
            )
            
            nav_items = self.get_nav_items()
            nav_rail = ft.Container(
                content=ft.Column([
                    ft.Container(height=25),
                    *[self.create_nav_item(item) for item in nav_items]
                ], spacing=5),
                bgcolor=self.colors["card"], 
                width=270, 
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                border=ft.border.only(right=ft.BorderSide(1, self.colors["border"]))
            )
            
            self.content_area = ft.Container(expand=True, padding=35, bgcolor=self.colors["bg"])
            
            # Stack para el menú desplegable
            main_content = ft.Stack([
                ft.Column([app_bar, ft.Row([nav_rail, self.content_area], expand=True, spacing=0)], spacing=0, expand=True),
                user_menu,
            ], expand=True)
            
            self.page.add(main_content)
            self.page.update()
            self.show_dashboard()
        except Exception as e:
            print(f"❌ Error en show_main_app: {e}")
            import traceback
            traceback.print_exc()

    def get_nav_items(self):
        """Retorna items del menú según el rol (Admin ve todo, Usuario también ve Caja)"""
        is_owner = self.user_data['rol'] in ['Dev', 'Admin']
        
        items = [{"icon": ft.Icons.DASHBOARD_ROUNDED, "label": "Dashboard", "view": "dashboard"}]
        
        # Todos los usuarios ven: Dashboard, Productos, Ventas y Caja
        items.append({"icon": ft.Icons.INVENTORY_2_ROUNDED, "label": "Productos", "view": "productos"})
        items.append({"icon": ft.Icons.SHOPPING_CART_ROUNDED, "label": "Punto de Venta", "view": "ventas"})
        items.append({"icon": ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "label": "Caja", "view": "caja"})
        
        # Solo Admin/Dev ven: Gastos, Métodos Pago, Reportes, Usuarios
        if is_owner:
            items.extend([
                {"icon": ft.Icons.RECEIPT_LONG_ROUNDED, "label": "Gastos", "view": "gastos"},
                {"icon": ft.Icons.CREDIT_CARD_ROUNDED, "label": "Métodos de Pago", "view": "metodos_pago"},
                {"icon": ft.Icons.ANALYTICS_ROUNDED, "label": "Reportes", "view": "reportes"},
                {"icon": ft.Icons.PEOPLE_ROUNDED, "label": "Usuarios", "view": "usuarios"},
            ])
        
        return items

    def create_nav_item(self, item):
        is_selected = self.current_view == item["view"]
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(item["icon"], size=22, color="white" if is_selected else self.colors["text_secondary"]),
                    width=40,
                    height=40,
                    bgcolor=self.colors["primary"] if is_selected else self.colors["bg"],
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Container(width=12),
                ft.Text(item["label"], size=15, color=self.colors["text_primary"], weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL)
            ]),
            padding=12, 
            margin=ft.margin.symmetric(vertical=3, horizontal=0),
            border_radius=12, 
            ink=True,
            on_click=lambda _, v=item["view"]: self.navigate_to(v),
            bgcolor=self.colors["card_hover"] if is_selected else None,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color="#00000008") if is_selected else None
        )

    def navigate_to(self, view):
        print(f"🔄 Navegando a: {view}")
        if self.current_view == view:
            print(f"   Ya está en {view}, refrescando...")
        
        self.current_view = view
        
        # Refrescar nav_rail para actualizar el item seleccionado
        self.refresh_nav_rail()
        
        # Cargar vista con refresh automático
        try:
            if view == "dashboard": self.show_dashboard()
            elif view == "productos": self.show_productos()
            elif view == "ventas": self.show_ventas()
            elif view == "caja": self.show_caja()
            elif view == "usuarios": self.show_usuarios()
            elif view == "gastos": self.show_gastos()
            elif view == "metodos_pago": self.show_metodos_pago()
            elif view == "reportes": self.show_reportes()
            print(f"✅ Vista {view} cargada")
        except Exception as e:
            print(f"❌ Error al navegar a {view}: {e}")
            import traceback
            traceback.print_exc()
            self.content_area.content = ft.Column([
                ft.Text(f"❌ Error al cargar {view}", size=24, weight=ft.FontWeight.BOLD, color=self.colors["danger"]),
                ft.Container(height=20),
                ft.Text(str(e), color=self.colors["text_secondary"]),
            ])
            self.page.update()
    
    def refresh_nav_rail(self):
        """Refresca el nav rail para actualizar el item seleccionado"""
        try:
            # Buscar el Container del nav_rail en la estructura de la página
            if self.page.controls and len(self.page.controls) > 0:
                main_col = self.page.controls[0]
                if hasattr(main_col, 'controls') and len(main_col.controls) > 1:
                    main_row = main_col.controls[1]
                    if hasattr(main_row, 'controls') and len(main_row.controls) > 0:
                        nav_container = main_row.controls[0]
                        if hasattr(nav_container, 'content'):
                            nav_items = self.get_nav_items()
                            nav_container.content.controls[1:] = [self.create_nav_item(item) for item in nav_items]
                            self.page.update()
        except Exception as e:
            print(f"⚠️ Error refrescando nav_rail: {e}")

    def show_dashboard(self):
        try:
            is_owner = self.user_data['rol'] in ['Dev', 'Admin']
            
            if is_owner:
                metrics = get_dashboard_metrics()
                ventas_str = str(metrics.get('ventas_mes', 0) or 0).replace('$', '').replace(',', '')
                gastos_str = str(metrics.get('gastos_mes', 0) or 0).replace('$', '').replace(',', '')
                ventas_mes = float(ventas_str)
                gastos_mes = float(gastos_str)
                balance = ventas_mes - gastos_mes
                stock_bajo = int(metrics.get('stock_bajo', 0) or 0)
                
                cards = ft.Row([
                    self.create_metric_card("💰 Ventas del Mes", f"${ventas_mes:,.2f}", self.colors["success"]),
                    self.create_metric_card("📉 Gastos del Mes", f"${gastos_mes:,.2f}", self.colors["danger"]),
                    self.create_metric_card("💵 Balance", f"${balance:,.2f}", 
                                           self.colors["primary"] if balance >= 0 else self.colors["danger"]),
                    self.create_metric_card("⚠️ Stock Bajo", str(stock_bajo), self.colors["warning"]),
                ], wrap=True, spacing=15)
                
                # Gráfico de ventas últimos 7 días
                labels, values = get_chart_data()
                chart_content = []
                if labels and values:
                    chart_content.append(ft.Container(height=25))
                    chart_content.append(ft.Row([
                        ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, color=self.colors["primary"], size=28),
                        ft.Container(width=10),
                        ft.Text("Ventas Últimos 7 Días", size=22, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                    ]))
                    chart_content.append(ft.Container(height=20))
                    
                    max_val = max(values) if values else 1
                    for i, (label, value) in enumerate(zip(labels, values)):
                        bar_width = (value / max_val) * 500 if max_val > 0 else 0
                        chart_content.append(ft.Row([
                            ft.Container(
                                content=ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=self.colors["text_secondary"]),
                                width=80,
                                alignment=ft.alignment.center_right,
                            ),
                            ft.Container(width=15),
                            ft.Container(
                                content=ft.Text(f"${value:,.0f}", size=13, color="white", weight=ft.FontWeight.W_500),
                                bgcolor=self.colors["primary"], 
                                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                                border_radius=8, 
                                width=max(bar_width, 60),
                                shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=self.colors["primary"] + "30")
                            ),
                        ], spacing=0))
                        chart_content.append(ft.Container(height=8))
            else:
                metrics = get_employee_metrics()
                cards = ft.Row([
                    self.create_metric_card("🛒 Ventas Hoy", str(metrics.get('ventas_hoy', 0)), self.colors["success"]),
                    self.create_metric_card("⚠️ Stock Bajo", str(metrics.get('stock_bajo', 0)), self.colors["warning"]),
                    self.create_metric_card("📦 Productos Activos", str(metrics.get('productos_activos', 0)), self.colors["info"]),
                ], wrap=True, spacing=15)
                chart_content = []
            
            content_widgets = [
                ft.Row([
                    ft.Column([
                        ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                        ft.Text(f"Bienvenido, {self.user_data.get('nombre_completo', self.user_data.get('nombre', 'Usuario'))}", 
                               size=15, color=self.colors["text_muted"]),
                    ], spacing=5),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.REFRESH_ROUNDED, 
                            tooltip="Refrescar datos",
                            on_click=lambda _: self.show_dashboard(),
                            icon_color=self.colors["primary"],
                            icon_size=24
                        ),
                        bgcolor=self.colors["primary_light"] + "20",
                        border_radius=10,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=25), 
                cards,
            ]
            
            if chart_content:
                content_widgets.append(ft.Container(
                    content=ft.Column(chart_content),
                    bgcolor=self.colors["card"], 
                    padding=30, 
                    border_radius=16,
                    border=ft.border.all(1, self.colors["border_light"]), 
                    margin=ft.margin.only(top=25),
                    shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 2))
                ))
            
            self.content_area.content = ft.Container(
                content=ft.Column(content_widgets, scroll=ft.ScrollMode.AUTO, expand=True),
                alignment=ft.alignment.top_center,
                expand=True,
            )
            self.page.update()
        except Exception as e:
            print(f"❌ Error en show_dashboard: {e}")
            import traceback
            traceback.print_exc()
            # Mostrar dashboard de error
            self.content_area.content = ft.Column([
                ft.Text("❌ Error al cargar el dashboard", size=24, weight=ft.FontWeight.BOLD, color=self.colors["danger"]),
                ft.Container(height=20),
                ft.Text(str(e), color=self.colors["text_secondary"]),
            ])
            self.page.update()

    def create_metric_card(self, title, value, color):
        # Selección de ícono según el tipo de métrica
        icon_map = {
            "Venta": ft.Icons.TRENDING_UP_ROUNDED,
            "Balance": ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED,
            "Gasto": ft.Icons.REMOVE_SHOPPING_CART_ROUNDED,
            "Cantidad": ft.Icons.RECEIPT_LONG_ROUNDED,
            "Stock": ft.Icons.INVENTORY_2_ROUNDED,
            "Producto": ft.Icons.CATEGORY_ROUNDED,
        }
        
        icon = ft.Icons.ANALYTICS_ROUNDED
        for key, value_icon in icon_map.items():
            if key in title:
                icon = value_icon
                break
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=26),
                        bgcolor=f"{color}12",
                        border_radius=12,
                        padding=12,
                    ),
                ]),
                ft.Container(height=18),
                ft.Text(title, size=13, color=self.colors["text_secondary"], weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                ft.Text(value, size=30, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
            ], spacing=0),
            bgcolor=self.colors["card"], 
            padding=28, 
            border_radius=16,
            border=ft.border.all(1, self.colors["border_light"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 2)),
            width=300,
        )

    def show_productos(self):
        print("📦 Cargando productos...")
        # Recargar configuración para asegurar que esté actualizada
        from app.auth import get_configuracion
        self.config = get_configuracion()
        productos, error = get_all_products()
        if error:
            print(f"❌ Error al obtener productos: {error}")
            self.show_snackbar(f"❌ Error: {error}", error=True)
            productos = []
        
        search_field = ft.TextField(
            label="Buscar producto",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            width=350,
            height=55,
            on_change=lambda e: self.filter_productos(e.control.value, self.categoria_filter.value if hasattr(self, 'categoria_filter') else None),
            border_radius=12,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
        )
        
        # Dropdown para filtrar por categoría - extraer categorías DIRECTAMENTE de los productos
        categoria_options = [ft.dropdown.Option("TODAS", "Todas las Categorías")]
        if productos:
            # Extraer categorías únicas de los productos (prod[3] es la categoría)
            categorias_unicas = set()
            for prod in productos:
                # prod[3] es NombreCategoria
                cat_nombre = str(prod[3]).strip()
                categorias_unicas.add(cat_nombre)
            
            # Agregar cada categoría al dropdown
            for cat_nombre in sorted(categorias_unicas):
                categoria_options.append(ft.dropdown.Option(cat_nombre, cat_nombre))
        
        self.categoria_filter = ft.Dropdown(
            label="Categoría",
            hint_text="Filtrar por categoría",
            width=220,
            value="TODAS",
            options=categoria_options,
            on_change=lambda e: self.filter_productos(search_field.value, e.control.value),
            border_radius=12,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
        )
        
        new_btn = ft.ElevatedButton(
            "Nuevo Producto", 
            icon=ft.Icons.ADD_ROUNDED,
            on_click=lambda e: self.new_producto_dialog(),
            bgcolor=self.colors["primary"], 
            color="white",
            height=55,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=25, vertical=15),
            )
        )
        
        refresh_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                tooltip="Refrescar lista",
                on_click=lambda _: self.show_productos(),
                icon_color=self.colors["primary"],
                icon_size=24
            ),
            bgcolor=self.colors["primary_light"] + "20",
            border_radius=10,
        )
        
        # Usar ListView en lugar de DataTable para mejor interactividad
        self.productos_list = ft.Column([], spacing=5, scroll=ft.ScrollMode.AUTO)
        self.all_productos = productos
        self.populate_productos_list(productos)
        
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Gestión de Productos", size=32, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                        ft.Text(f"{len(productos)} producto{'s' if len(productos) != 1 else ''} registrado{'s' if len(productos) != 1 else ''}", 
                               size=15, color=self.colors["text_muted"]),
                    ], spacing=5),
                    ft.Container(expand=True),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=15),
                ft.Row([
                    search_field,
                    ft.Container(width=10),
                    self.categoria_filter,
                    ft.Container(expand=True),
                    refresh_btn,
                    ft.Container(width=10),
                    new_btn
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=25),
                ft.Container(
                    content=self.productos_list,
                    border=ft.border.all(1, self.colors["border_light"]), 
                    border_radius=16,
                    padding=20, 
                    bgcolor=self.colors["card"], 
                    expand=True,
                    shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 2))
                ),
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            alignment=ft.alignment.center,
            expand=True,
        )
        self.page.update()
    
    def populate_productos_list(self, productos):
        self.productos_list.controls.clear()
        
        if not productos:
            self.productos_list.controls.append(
                ft.Container(
                    content=ft.Text("No hay productos para mostrar", 
                                  color=self.colors["text_secondary"], size=16),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
        else:
            # Header
            header_row = [
                ft.Text("Código", weight=ft.FontWeight.W_600, width=100, size=13, color=self.colors["text_muted"]),
                ft.Text("Nombre", weight=ft.FontWeight.W_600, width=180, size=13, color=self.colors["text_muted"]),
                ft.Text("Categoría", weight=ft.FontWeight.W_600, width=130, size=13, color=self.colors["text_muted"]),
            ]
            
            # Agregar columna de código de barra si está habilitado
            if self.config and self.config.get('usar_codigos_barra', False):
                header_row.append(ft.Text("Cód. Barra", weight=ft.FontWeight.W_600, width=110, size=13, color=self.colors["text_muted"]))
            
            header_row.extend([
                ft.Text("Precio", weight=ft.FontWeight.W_600, width=100, size=13, color=self.colors["text_muted"]),
                ft.Text("Stock", weight=ft.FontWeight.W_600, width=80, size=13, color=self.colors["text_muted"]),
                ft.Text("Acciones", weight=ft.FontWeight.W_600, width=200, size=13, color=self.colors["text_muted"]),
            ])
            
            self.productos_list.controls.append(
                ft.Container(
                    content=ft.Row(header_row),
                    bgcolor=self.colors["bg"],
                    padding=15,
                    border_radius=10
                )
            )
            
            # Productos
            for prod in productos:
                precio_val = float(str(prod[4]).replace('$', '').replace(',', '')) if prod[4] else 0.0
                stock_val = int(prod[5]) if prod[5] else 0
                codigo_barra = prod[6] if len(prod) > 6 else None
                stock_color = self.colors["danger"] if stock_val < 5 else (
                    self.colors["warning"] if stock_val < 15 else self.colors["text_primary"])
                
                # Crear funciones específicas para este producto
                def make_edit_handler(product):
                    def handler(e):
                        self.edit_producto_dialog(product)
                    return handler
                
                def make_delete_handler(product):
                    def handler(e):
                        self.delete_producto_confirm(product)
                    return handler
                
                # Construir fila de producto
                product_row = [
                    ft.Text(str(prod[1]), width=100, size=14),
                    ft.Text(str(prod[2]), width=180, size=14, weight=ft.FontWeight.W_500),
                    ft.Container(
                        content=ft.Text(str(prod[3]), size=12, color=self.colors["primary"]),
                        bgcolor=self.colors["primary_light"] + "20",
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=8,
                    ),
                ]
                
                # Agregar código de barra si está habilitado
                if self.config and self.config.get('usar_codigos_barra', False):
                    if codigo_barra:
                        product_row.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.QR_CODE_SCANNER, size=16, color=self.colors["success"]),
                                    ft.Text(codigo_barra, size=12, color=self.colors["text_secondary"])
                                ], spacing=5),
                                width=110
                            )
                        )
                    else:
                        product_row.append(ft.Text("-", width=110, size=13, color=self.colors["text_muted"]))
                
                product_row.extend([
                    ft.Container(width=5),
                    ft.Text(f"${precio_val:,.2f}", width=95, size=14, weight=ft.FontWeight.W_500),
                    ft.Container(
                        content=ft.Text(str(stock_val), size=13, color="white", weight=ft.FontWeight.BOLD),
                        bgcolor=stock_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=8,
                        alignment=ft.alignment.center,
                        width=65,
                    ),
                    ft.Container(width=5),
                    ft.Row([
                        ft.ElevatedButton(
                            "Editar",
                            icon=ft.Icons.EDIT_ROUNDED,
                            bgcolor=self.colors["info"],
                            color="white",
                            on_click=make_edit_handler(prod),
                            height=38,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            )
                        ),
                        ft.ElevatedButton(
                            "Eliminar",
                            icon=ft.Icons.DELETE_ROUNDED,
                            bgcolor=self.colors["danger"],
                            color="white",
                            on_click=make_delete_handler(prod),
                            height=38,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            )
                        ),
                    ], spacing=8, width=200),
                ])
                
                self.productos_list.controls.append(
                    ft.Container(
                        content=ft.Row(product_row, alignment=ft.MainAxisAlignment.START),
                        padding=15,
                        border=ft.border.only(bottom=ft.BorderSide(1, self.colors["border_light"])),
                        ink=True,
                        on_hover=lambda e: setattr(e.control, 'bgcolor', self.colors["bg"] if e.data == "true" else None) or self.page.update(),
                    )
                )
    
    def filter_productos(self, search_term, categoria=None):
        """Filtra productos por término de búsqueda y/o categoría"""
        filtered = self.all_productos
        
        # Filtrar por categoría si no es "TODAS"
        if categoria and categoria != "TODAS":
            # prod[3] es el nombre de la categoría (string)
            filtered = [p for p in filtered if str(p[3]).strip() == str(categoria).strip()]
        
        # Filtrar por término de búsqueda
        if search_term:
            term_lower = search_term.lower()
            filtered = [p for p in filtered 
                       if term_lower in str(p[1]).lower() or term_lower in str(p[2]).lower()]
        
        self.populate_productos_list(filtered)
        self.page.update()

    def new_producto_dialog(self):
        # Cargar configuración si no está disponible
        if not self.config:
            from app.auth import get_configuracion
            self.config = get_configuracion()
        
        categorias, _ = get_all_categories()
        
        usar_codigos_sistema = self.config and self.config.get('usar_codigos_barra', False)
        
        # Ajustar label según si se usan códigos de barra
        codigo_label = "Código interno (opcional)" if usar_codigos_sistema else "Código *"
        codigo_field = ft.TextField(label=codigo_label, width=400, max_length=50)
        nombre_field = ft.TextField(label="Nombre *", width=400, max_length=200)
        cat_dropdown = ft.Dropdown(label="Categoría *", width=400,
            options=[ft.dropdown.Option(str(c[0]), c[1]) for c in categorias] if categorias else [],
            hint_text="Seleccionar categoría...")
        precio_field = ft.TextField(label="Precio *", width=400, keyboard_type=ft.KeyboardType.NUMBER,
                                   hint_text="0.00")
        stock_field = ft.TextField(label="Stock *", width=400, keyboard_type=ft.KeyboardType.NUMBER,
                                  hint_text="0")
        
        # Campos de código de barra (solo si el sistema tiene habilitados códigos de barra)
        usar_codigo_barra_checkbox = None
        codigo_barra_field = None
        codigo_barra_container = None
        
        if usar_codigos_sistema:
            # Checkbox para activar código de barra en este producto
            usar_codigo_barra_checkbox = ft.Checkbox(
                label="Este producto usa código de barra",
                value=False,
                on_change=lambda e: toggle_codigo_barra(e.control.value)
            )
            
            # Campo de código de barra (inicialmente oculto)
            codigo_barra_field = ft.TextField(
                label="Código de Barra", 
                width=400, 
                max_length=50,
                hint_text="Escanee o ingrese el código de barra",
                visible=False
            )
            
            codigo_barra_container = ft.Container(
                content=ft.Column([
                    usar_codigo_barra_checkbox,
                    codigo_barra_field
                ], spacing=10),
                padding=ft.padding.only(top=10, bottom=10),
                border=ft.border.all(1, self.colors["border_light"]),
                border_radius=8,
                bgcolor=self.colors["info_light"]
            )
        
        def toggle_codigo_barra(usar):
            if codigo_barra_field:
                codigo_barra_field.visible = usar
                # Ocultar/mostrar campo de código interno
                codigo_field.visible = not usar
                if not usar:
                    codigo_barra_field.value = ""
                    codigo_field.visible = True
                self.page.update()
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def validate_and_save(e):
            nombre = nombre_field.value.strip() if nombre_field.value else ""
            codigo = codigo_field.value.strip() if codigo_field.value else ""
            
            # Validar solo campos obligatorios (nombre y categoría)
            if not nombre or not cat_dropdown.value:
                self.show_snackbar("⚠️ Complete todos los campos requeridos (*)", error=True)
                return
            
            # Validar longitudes si hay valores
            if codigo and len(codigo) > 50:
                self.show_snackbar("⚠️ El código no puede exceder 50 caracteres", error=True)
                return
            
            if len(nombre) > 200:
                self.show_snackbar("⚠️ El nombre no puede exceder 200 caracteres", error=True)
                return
            
            # Validar caracteres especiales
            if any(char in nombre for char in ["'", '"', ";", "--", "/*", "*/"]):
                self.show_snackbar("⚠️ El nombre no puede contener comillas, punto y coma o caracteres SQL", error=True)
                return
            
            if codigo and any(char in codigo for char in ["'", '"', ";", "--", "/*", "*/"]):
                self.show_snackbar("⚠️ El código no puede contener comillas, punto y coma o caracteres SQL", error=True)
                return
            
            # Validar código de barra si está habilitado
            codigo_barra_val = None
            if usar_codigo_barra_checkbox and usar_codigo_barra_checkbox.value:
                if codigo_barra_field and codigo_barra_field.value:
                    codigo_barra_val = codigo_barra_field.value.strip()
                    if len(codigo_barra_val) > 50:
                        self.show_snackbar("⚠️ El código de barra no puede exceder 50 caracteres", error=True)
                        return
                else:
                    self.show_snackbar("⚠️ Debe ingresar el código de barra o desmarcar la opción", error=True)
                    return
            
            try:
                precio_val = float(precio_field.value) if precio_field.value else 0
                stock_val = int(stock_field.value) if stock_field.value else 0
                
                if precio_val <= 0:
                    self.show_snackbar("⚠️ El precio debe ser mayor a 0", error=True)
                    return
                
                if stock_val < 0:
                    self.show_snackbar("⚠️ El stock no puede ser negativo", error=True)
                    return
                
                success, msg = create_product(codigo, nombre,
                    int(cat_dropdown.value) if cat_dropdown.value else None,
                    precio_val, stock_val, codigo_barra_val)
                
                if success:
                    self.show_snackbar(f"✅ {msg}")
                    close_overlay()
                    self.show_productos()
                else:
                    self.show_snackbar(f"❌ {msg}", error=True)
            except ValueError:
                self.show_snackbar("⚠️ Precio y stock deben ser números válidos", error=True)
            except Exception as e:
                self.show_snackbar(f"❌ Error: {str(e)}", error=True)
        
        # Crear overlay con diálogo modal
        # Lista de campos del formulario
        form_fields = [
            codigo_field, 
            nombre_field, 
            cat_dropdown, 
            precio_field, 
            stock_field
        ]
        
        # Agregar sección de código de barra si está habilitado
        if codigo_barra_container:
            form_fields.append(codigo_barra_container)
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ADD_BOX_ROUNDED, color=self.colors["primary"], size=32),
                    ft.Container(width=12),
                    ft.Text("Nuevo Producto", size=24, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, on_click=close_overlay, icon_size=24, 
                                 icon_color=self.colors["text_secondary"])
                ], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=20, color=self.colors["border_light"]),
                ft.Container(height=10),
                ft.Text("Campos marcados con * son obligatorios", size=12, color=self.colors["text_muted"], italic=True),
                ft.Container(height=15),
                *form_fields,
                ft.Container(height=25),
                ft.Row([
                    ft.OutlinedButton(
                        "Cancelar", 
                        on_click=close_overlay,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(horizontal=25, vertical=15),
                        ),
                        height=45,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Guardar Producto", 
                        icon=ft.Icons.SAVE_ROUNDED,
                        on_click=validate_and_save,
                        bgcolor=self.colors["success"], 
                        color="white",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(horizontal=25, vertical=15),
                        ),
                        height=45,
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=550,
            bgcolor=self.colors["card"],
            padding=35,
            border_radius=16,
            border=ft.border.all(1, self.colors["border_light"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=30, color="#00000020", offset=ft.Offset(0, 10))
        )
        
        self.overlay_dialog = ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True
        )
        
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()
        print("✅ Diálogo overlay creado y visible")

    def edit_producto_dialog(self, producto):
        print(f"📝 Iniciando edición de producto {producto[0]}")
        try:
            # Obtener datos completos del producto
            product_data, error = get_product_by_id(producto[0])
            print(f"   Datos obtenidos: {product_data}, Error: {error}")
            if error or not product_data:
                self.show_snackbar(f"❌ Error: No se pudieron cargar los datos del producto", error=True)
                return
            
            categorias, _ = get_all_categories()
            precio_val = float(str(producto[4]).replace('$', '').replace(',', '')) if producto[4] else 0.0
            
            codigo_field = ft.TextField(label="Código *", width=400, value=producto[1], max_length=50)
            nombre_field = ft.TextField(label="Nombre *", width=400, value=producto[2], max_length=200)
            cat_dropdown = ft.Dropdown(label="Categoría *", width=400,
                options=[ft.dropdown.Option(str(c[0]), c[1]) for c in categorias] if categorias else [],
                value=str(product_data[2]))  # Preseleccionar categoría actual (idCategoria)
            precio_field = ft.TextField(label="Precio *", width=400, value=str(precio_val),
                                       keyboard_type=ft.KeyboardType.NUMBER)
            stock_field = ft.TextField(label="Stock *", width=400, value=str(producto[5]),
                                      keyboard_type=ft.KeyboardType.NUMBER)
            print("   Campos creados correctamente")
            
            def close_overlay(e=None):
                if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                    self.page.overlay.remove(self.overlay_dialog)
                    self.page.update()
            
            def validate_and_save(_):
                codigo = codigo_field.value.strip() if codigo_field.value else ""
                nombre = nombre_field.value.strip() if nombre_field.value else ""
                
                if not codigo or not nombre or not cat_dropdown.value:
                    self.show_snackbar("⚠️ Complete todos los campos requeridos (*)", error=True)
                    return
                
                if len(codigo) > 50:
                    self.show_snackbar("⚠️ El código no puede exceder 50 caracteres", error=True)
                    return
                
                if len(nombre) > 200:
                    self.show_snackbar("⚠️ El nombre no puede exceder 200 caracteres", error=True)
                    return
                
                if any(char in codigo + nombre for char in ["'", '"', ";", "--", "/*", "*/"]):
                    self.show_snackbar("⚠️ El código y nombre no pueden contener caracteres SQL inválidos", error=True)
                    return
                
                try:
                    precio_val = float(precio_field.value) if precio_field.value else 0
                    stock_val = int(stock_field.value) if stock_field.value else 0
                    
                    if precio_val <= 0:
                        self.show_snackbar("⚠️ El precio debe ser mayor a 0", error=True)
                        return
                    
                    if stock_val < 0:
                        self.show_snackbar("⚠️ El stock no puede ser negativo", error=True)
                        return
                    
                    success, msg = update_product(producto[0], codigo, nombre,
                        int(cat_dropdown.value) if cat_dropdown.value else None,
                        precio_val, stock_val)
                    
                    if success:
                        self.show_snackbar(f"✅ {msg}")
                        close_overlay()
                        self.show_productos()
                    else:
                        self.show_snackbar(f"❌ {msg}", error=True)
                except ValueError:
                    self.show_snackbar("⚠️ Precio y stock deben ser números válidos", error=True)
                except Exception as e:
                    self.show_snackbar(f"❌ Error: {str(e)}", error=True)
        
            # Crear overlay
            dialog_content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"✏️ Editar: {producto[2]}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay, icon_size=20)
                    ]),
                    ft.Divider(height=20, color=self.colors["border"]),
                    ft.Text("Campos marcados con * son obligatorios", size=12, color=self.colors["text_secondary"]),
                    ft.Container(height=10),
                    codigo_field, nombre_field, cat_dropdown, precio_field, stock_field,
                    ft.Container(height=20),
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=close_overlay),
                        ft.Container(expand=True),
                        ft.ElevatedButton("Guardar Cambios", on_click=validate_and_save,
                                        bgcolor=self.colors["info"], color="white")
                    ], alignment=ft.MainAxisAlignment.END)
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=500,
                bgcolor=self.colors["card"],
                padding=30,
                border_radius=12,
                border=ft.border.all(2, self.colors["border"]),
                shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
            )
            
            self.overlay_dialog = ft.Container(
                content=dialog_content,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                expand=True
            )
            
            self.page.overlay.append(self.overlay_dialog)
            self.page.update()
            print("✅ Diálogo de edición overlay creado")
        
        except Exception as e:
            print(f"❌ Error en edit_producto_dialog: {e}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Error: {str(e)}", error=True)

    def delete_producto_confirm(self, producto):
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def confirm_delete(_):
            success, msg = delete_product(producto[0])
            self.show_snackbar(msg, not success)
            if success: close_overlay(); self.show_productos()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=self.colors["danger"], size=40),
                    ft.Container(width=15),
                    ft.Text("Confirmar Eliminación", size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                ft.Text(f"¿Estás seguro de eliminar el producto '{producto[2]}'?", size=16),
                ft.Text("Esta acción no se puede deshacer.", size=12, color=self.colors["text_secondary"], italic=True),
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Eliminar", on_click=confirm_delete,
                                    bgcolor=self.colors["danger"], color="white", icon=ft.Icons.DELETE)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=450,
            bgcolor=self.colors["card"],
            padding=30,
            border_radius=12,
            border=ft.border.all(2, self.colors["danger"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        
        self.overlay_dialog = ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True
        )
        
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def show_ventas(self):
        # Recargar configuración si es necesario
        if not self.config:
            from app.auth import get_configuracion
            self.config = get_configuracion()
        
        self.cart_items = []
        self.search_timer = None
        
        def on_search_change(e):
            # Implementar debounce de 300ms como PyQt6
            if self.search_timer:
                self.search_timer.cancel()
            import threading
            self.search_timer = threading.Timer(0.3, lambda: self.search_productos_ventas(e.control.value))
            self.search_timer.start()
        
        def on_search_submit(e):
            # Detectar escaneo de código de barra (Enter presionado)
            term = e.control.value.strip()
            if term:
                print(f"🔍 Búsqueda por Enter/Scanner: {term}")
                self.buscar_y_agregar_producto(term, e.control)
        
        usar_codigos = self.config and self.config.get('usar_codigos_barra', False)
        hint_text = "Escanee código de barra o escriba nombre..." if usar_codigos else "Escribe código o nombre (mínimo 2 caracteres)..."
        
        search_field = ft.TextField(
            label="🔍 Buscar producto",
            hint_text=hint_text,
            width=450,
            on_change=on_search_change,
            on_submit=on_search_submit,
            autofocus=True
        )
        
        self.productos_list = ft.Column([], scroll=ft.ScrollMode.AUTO, height=350)
        self.cart_list = ft.Column([], scroll=ft.ScrollMode.AUTO, height=350)
        
        from app.database import get_connection
        metodos = []
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT idMetodoPago, Nombre FROM MetodosPago WHERE Activo = 1")
                metodos = cursor.fetchall()
                cursor.close(); conn.close()
        except Exception as e: print(f"Error métodos de pago: {e}")
        
        self.metodo_pago_dropdown = ft.Dropdown(
            label="💳 Método de Pago",
            width=350,
            hint_text="Seleccionar...",
            options=[ft.dropdown.Option(str(m[0]), m[1]) for m in metodos]
        )
        
        self.total_label = ft.Text("TOTAL: $0.00", size=28, weight=ft.FontWeight.BOLD,
                                   color=self.colors["primary"])
        
        finalizar_btn = ft.ElevatedButton(
            "Finalizar Venta",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=lambda _: self.finalizar_venta(),
            bgcolor=self.colors["success"],
            color="white",
            width=350,
            height=55,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        
        cancelar_btn = ft.OutlinedButton(
            "Cancelar",
            icon=ft.Icons.CLOSE,
            on_click=lambda _: self.clear_cart(),
            width=350,
            height=45
        )
        
        # Mostrar mensaje inicial
        self.productos_list.controls = [
            ft.Container(
                content=ft.Text("Escriba 2+ caracteres para buscar...",
                              color=self.colors["text_secondary"], size=14),
                alignment=ft.alignment.center,
                padding=20
            )
        ]
        
        self.content_area.content = ft.Column([
            ft.Row([
                ft.Text("🛒 Punto de Venta", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Limpiar",
                             on_click=lambda _: self.show_ventas(),
                             icon_color=self.colors["primary"])
            ]),
            ft.Container(height=20),
            ft.Row([
                # Panel de búsqueda
                ft.Container(
                    content=ft.Column([
                        ft.Text("Buscar Productos", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        search_field,
                        ft.Container(height=10),
                        self.productos_list,
                    ]),
                    bgcolor=self.colors["card"],
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, self.colors["border"]),
                    expand=2
                ),
                ft.Container(width=20),
                # Panel de carrito
                ft.Container(
                    content=ft.Column([
                        ft.Text("Carrito de Venta", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        self.cart_list,
                        ft.Divider(height=20, color=self.colors["border"]),
                        self.metodo_pago_dropdown,
                        ft.Container(height=15),
                        self.total_label,
                        ft.Container(height=20),
                        finalizar_btn,
                        ft.Container(height=10),
                        cancelar_btn,
                    ]),
                    bgcolor=self.colors["card"],
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, self.colors["border"]),
                    expand=1
                ),
            ], expand=True),
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()
    
    def clear_cart(self):
        self.cart_items = []
        self.update_cart_display()
        self.show_snackbar("🗑️ Carrito limpiado")

    def buscar_y_agregar_producto(self, term, search_field):
        """Busca un producto por código de barra y lo agrega automáticamente al carrito"""
        productos, error = search_products(term)
        
        if error:
            self.show_snackbar(f"❌ Error: {error}", error=True)
            return
        
        if not productos:
            self.show_snackbar(f"⚠️ No se encontró producto: {term}", error=True)
            return
        
        # Si hay un solo resultado (código de barra exacto), agregarlo al carrito
        if len(productos) == 1:
            producto = productos[0]
            self.add_to_cart(producto)
            self.show_snackbar(f"✅ {producto.NombreProducto} agregado")
            # Limpiar campo de búsqueda para siguiente escaneo
            search_field.value = ""
            search_field.focus()
            self.page.update()
        else:
            # Múltiples resultados, mostrar lista
            self.search_productos_ventas(term)
    
    def search_productos_ventas(self, term):
        if len(term) < 2:
            self.productos_list.controls = [
                ft.Container(
                    content=ft.Text("Escriba 2+ caracteres para buscar...",
                                  color=self.colors["text_secondary"], size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
            self.page.update()
            return
        
        productos, error = search_products(term)
        if error or not productos:
            self.productos_list.controls = [
                ft.Container(
                    content=ft.Text("No se encontraron productos" if not error else f"Error: {error}",
                                  color=self.colors["text_secondary"], size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
            self.page.update()
            return
        
        self.productos_list.controls = []
        for prod in productos:
            stock_color = self.colors["danger"] if prod.Stock < 5 else (
                self.colors["warning"] if prod.Stock < 15 else self.colors["success"])
            
            prod_card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(prod.NombreProducto, weight=ft.FontWeight.BOLD, size=14),
                        ft.Row([
                            ft.Text(f"{prod.Codigo}", size=12, color=self.colors["text_secondary"]),
                            ft.Text("•", size=12, color=self.colors["text_secondary"]),
                            ft.Text(f"Stock: {prod.Stock}", size=12, color=stock_color, weight=ft.FontWeight.BOLD),
                        ], spacing=5),
                    ], expand=True),
                    ft.Text(f"${float(prod.Precio):,.2f}", weight=ft.FontWeight.BOLD, size=16,
                           color=self.colors["primary"]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=12,
                border=ft.border.all(1, self.colors["border"]),
                border_radius=8,
                bgcolor=ft.Colors.WHITE,
                margin=ft.margin.only(bottom=5),
                on_click=lambda _, p=prod: self.add_to_cart(p),
                ink=True,
                on_hover=lambda e: self.hover_product_card(e),
            )
            self.productos_list.controls.append(prod_card)
        
        self.page.update()
    
    def hover_product_card(self, e):
        if e.data == "true":
            e.control.bgcolor = ft.Colors.BLUE_50
            e.control.elevation = 2
        else:
            e.control.bgcolor = ft.Colors.WHITE
            e.control.elevation = 0
        e.control.update()

    def add_to_cart(self, producto):
        pid = producto.idProducto
        existing = None
        for item in self.cart_items:
            if item['id'] == pid: existing = item; break
        
        if existing:
            if existing['quantity'] < producto.Stock:
                existing['quantity'] += 1
                existing['subtotal'] = existing['quantity'] * existing['price']
            else: self.show_snackbar(f"⚠️ No hay más stock para {producto.NombreProducto}", error=True)
        else:
            if producto.Stock > 0:
                self.cart_items.append({'id': pid, 'name': producto.NombreProducto,
                    'price': float(producto.Precio), 'quantity': 1, 'stock_max': producto.Stock,
                    'subtotal': float(producto.Precio)})
            else: self.show_snackbar(f"⚠️ {producto.NombreProducto} sin stock", error=True)
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_list.controls.clear()
        
        if not self.cart_items:
            self.cart_list.controls.append(
                ft.Container(
                    content=ft.Text("Carrito vacío", color=self.colors["text_secondary"], size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            total = 0
        else:
            for item in self.cart_items:
                qty_field = ft.TextField(
                    value=str(item['quantity']),
                    width=70,
                    height=40,
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    on_change=lambda e, i=item: self.update_quantity(i, e.control.value),
                    border_color=self.colors["primary"]
                )
                
                self.cart_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(item['name'], weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(f"${item['price']:,.2f} c/u", 
                                           size=12, color=self.colors["text_secondary"]),
                                ], expand=True),
                                qty_field,
                            ]),
                            ft.Container(height=5),
                            ft.Row([
                                ft.Text(f"Subtotal: ${item['subtotal']:,.2f}",
                                       weight=ft.FontWeight.BOLD, color=self.colors["primary"]),
                                ft.Container(expand=True),
                                ft.TextButton(
                                    "Eliminar",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=self.colors["danger"],
                                    on_click=lambda _, i=item: self.remove_from_cart(i),
                                    style=ft.ButtonStyle(color=self.colors["danger"])
                                ),
                            ]),
                        ]),
                        padding=12,
                        border=ft.border.all(1, self.colors["border"]),
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                        margin=ft.margin.only(bottom=8)
                    )
                )
            total = sum(item['subtotal'] for item in self.cart_items)
        
        self.total_label.value = f"TOTAL: ${total:,.2f}"
        self.page.update()

    def update_quantity(self, item, new_qty):
        try:
            qty = int(new_qty)
            if qty > 0 and qty <= item['stock_max']:
                item['quantity'] = qty; item['subtotal'] = qty * item['price']
                self.update_cart_display()
        except: pass

    def remove_from_cart(self, item):
        self.cart_items.remove(item); self.update_cart_display()

    def finalizar_venta(self):
        if not self.cart_items: 
            self.show_snackbar("⚠️ El carrito está vacío", error=True)
            return
        
        if not self.metodo_pago_dropdown.value: 
            self.show_snackbar("⚠️ Seleccione un método de pago", error=True)
            return
        
        # Verificar que haya caja abierta
        from app.caja_logic import get_caja_activa
        caja_activa, err = get_caja_activa()
        
        if err or not caja_activa:
            self.show_snackbar("⚠️ Debe abrir una caja para procesar ventas", error=True)
            return
        
        if caja_activa[3] != 'Abierta':  # Estado != Abierta
            self.show_snackbar("⚠️ La caja está pausada. Reanúdela para procesar ventas", error=True)
            return
        
        success, msg = process_sale(self.cart_items, self.user_data['id'], int(self.metodo_pago_dropdown.value))
        self.show_snackbar(msg, not success)
        if success:
            self.cart_items = []
            self.update_cart_display()
            # Limpiar búsqueda
            self.productos_list.controls = [
                ft.Container(
                    content=ft.Text("Escriba 2+ caracteres para buscar...",
                                  color=self.colors["text_secondary"], size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
            self.page.update()

    def show_caja(self):
        caja_activa, err = get_caja_activa()
        
        content_parts = [ft.Text("Gestión de Caja", size=28, weight=ft.FontWeight.BOLD), ft.Container(height=20)]
        
        # Verificar si ya se realizó el cierre formal de hoy
        is_cerrado, msg_cerrado = check_cierre_realizado_hoy()
        cierre_status_text = msg_cerrado
        cierre_status_color = self.colors["danger"] if is_cerrado else self.colors["success"]
        
        # Mostrar estado de cierre formal
        content_parts.append(ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EVENT_NOTE, color=cierre_status_color, size=28),
                ft.Container(width=10),
                ft.Text(f"Cierre Formal: {cierre_status_text}", size=15, 
                       weight=ft.FontWeight.BOLD, color=cierre_status_color)
            ]),
            bgcolor=self.colors["card"], padding=15, border_radius=10,
            border=ft.border.all(1, cierre_status_color)
        ))
        content_parts.append(ft.Container(height=20))
        
        if err:
            content_parts.append(ft.Container(
                content=ft.Text(f"❌ Error: {err}", color=self.colors["danger"]),
                bgcolor=self.colors["card"], padding=20, border_radius=12))
        elif caja_activa:
            # caja_activa es una tupla: (idCaja, FechaCaja, Turno, Estado, idUsuarioApertura, FechaHoraApertura, idUsuarioCierre, FechaHoraCierre)
            estado = caja_activa[3]  # Estado
            turno = caja_activa[2]   # Turno
            fecha_apertura = caja_activa[5].strftime("%Y-%m-%d %H:%M") if caja_activa[5] else "N/A"
            
            estado_color = self.colors["success"] if estado == 'Abierta' else self.colors["warning"]
            info_text = f"Estado: {estado}\nTurno: {turno}\nApertura: {fecha_apertura}"
            
            buttons = []
            if estado == 'Abierta':
                buttons.append(ft.ElevatedButton("Pausar Caja", icon=ft.Icons.PAUSE,
                    on_click=lambda _: self.pausar_caja_action(), bgcolor=self.colors["warning"], color="white"))
            elif estado == 'Pausada':
                buttons.append(ft.ElevatedButton("Reanudar Caja", icon=ft.Icons.PLAY_ARROW,
                    on_click=lambda _: self.reanudar_caja_action(), bgcolor=self.colors["info"], color="white"))
            
            # Solo permitir cerrar caja si NO se realizó el cierre formal hoy
            if is_cerrado:
                buttons.append(ft.ElevatedButton("Cerrar Caja (Ya cerrado hoy)", icon=ft.Icons.LOCK,
                    disabled=True, bgcolor=self.colors["text_secondary"], color="white"))
            else:
                buttons.append(ft.ElevatedButton("Cerrar Caja", icon=ft.Icons.LOCK,
                    on_click=lambda _: self.cerrar_caja_action(), bgcolor=self.colors["danger"], color="white"))
            
            content_parts.append(ft.Container(content=ft.Column([
                ft.Text(f"Caja {estado}", size=24, weight=ft.FontWeight.BOLD, color=estado_color),
                ft.Container(height=10), ft.Text(info_text, size=16), ft.Container(height=20),
                ft.Row(buttons, spacing=10),
            ]), bgcolor=self.colors["card"], padding=30, border_radius=12, border=ft.border.all(1, self.colors["border"])))
            
            # Mostrar resumen de la caja activa
            resumen, err_res = get_resumen_caja_activa()
            if not err_res and resumen:
                ventas_cards = ft.Row([
                    self.create_metric_card("💰 Total Ventas", f"${resumen['ventas_total']:,.2f}", self.colors["success"]),
                    self.create_metric_card("📉 Total Gastos", f"${resumen['gastos_total']:,.2f}", self.colors["danger"]),
                    self.create_metric_card("💵 Balance", f"${resumen['balance_neto']:,.2f}",
                        self.colors["primary"] if resumen['balance_neto'] >= 0 else self.colors["danger"]),
                ], wrap=True, spacing=15)
                
                content_parts.extend([ft.Container(height=20), 
                    ft.Text("Resumen de Caja Activa", size=20, weight=ft.FontWeight.BOLD), 
                    ft.Container(height=10), ventas_cards])
                
                # Desglose por método de pago
                if resumen['ventas_desglose']:
                    content_parts.append(ft.Container(height=20))
                    content_parts.append(ft.Text("Ventas por Método de Pago", size=18, weight=ft.FontWeight.BOLD))
                    for metodo_data in resumen['ventas_desglose']:
                        metodo_nombre = metodo_data[0]  # Nombre
                        metodo_total = float(metodo_data[1])  # TotalPorMetodo
                        content_parts.append(ft.Container(
                            content=ft.Row([
                                ft.Text(metodo_nombre, expand=True),
                                ft.Text(f"${metodo_total:,.2f}", weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10, bgcolor=self.colors["card"], border_radius=8,
                            border=ft.border.all(1, self.colors["border"]), margin=ft.margin.symmetric(vertical=3)
                        ))
        else:
            # No hay caja activa
            content_parts.append(ft.Container(content=ft.Column([
                ft.Text("Sin Caja Activa", size=24, weight=ft.FontWeight.BOLD, color=self.colors["text_secondary"]),
                ft.Container(height=20), ft.Text("No hay una caja abierta actualmente", size=16), 
                ft.Container(height=30),
                ft.ElevatedButton("Abrir Caja", icon=ft.Icons.LOCK_OPEN,
                    on_click=lambda _: self.abrir_caja_action(), bgcolor=self.colors["success"], color="white"),
            ]), bgcolor=self.colors["card"], padding=40, border_radius=12, border=ft.border.all(1, self.colors["border"])))
        
        # Mostrar historial de cierres formales (CierresDeCaja)
        historial_cierres, err_cierres = get_historial_cierres()
        if not err_cierres and historial_cierres:
            content_parts.extend([ft.Container(height=30), 
                ft.Text("📋 Historial de Cierres Formales", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Últimos cierres registrados en CierresDeCaja", size=13, color=self.colors["text_secondary"]),
                ft.Container(height=10)])
            
            cierres_table = ft.DataTable(columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ventas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Gastos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Balance", weight=ft.FontWeight.BOLD)),
            ], rows=[])
            
            for cierre_record in historial_cierres[:20]:  # Mostrar últimos 20
                # (FechaCierre, NombreCompleto, TotalVentas, TotalGastos, BalanceNeto)
                fecha_cierre = cierre_record[0].strftime("%Y-%m-%d") if cierre_record[0] else ""
                nombre_usuario = cierre_record[1] or ""
                ventas = float(cierre_record[2]) if cierre_record[2] else 0.0
                gastos = float(cierre_record[3]) if cierre_record[3] else 0.0
                balance = float(cierre_record[4]) if cierre_record[4] else 0.0
                balance_color = self.colors["success"] if balance >= 0 else self.colors["danger"]
                
                cierres_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(fecha_cierre)),
                    ft.DataCell(ft.Text(nombre_usuario)),
                    ft.DataCell(ft.Text(f"${ventas:,.2f}", color=self.colors["success"])),
                    ft.DataCell(ft.Text(f"${gastos:,.2f}", color=self.colors["danger"])),
                    ft.DataCell(ft.Text(f"${balance:,.2f}", color=balance_color, weight=ft.FontWeight.BOLD)),
                ]))
            
            content_parts.append(ft.Container(
                content=ft.Column([cierres_table], scroll=ft.ScrollMode.AUTO),
                border=ft.border.all(1, self.colors["border"]), border_radius=8,
                padding=15, bgcolor=self.colors["card"]))
        
        # Mostrar historial de cajas operativas cerradas
        historial, err_hist = get_historial_cajas(10)
        if not err_hist and historial:
            content_parts.extend([ft.Container(height=30), 
                ft.Text("🗂️ Historial de Cajas Operativas", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Últimas 10 cajas cerradas (Tabla Cajas)", size=13, color=self.colors["text_secondary"]),
                ft.Container(height=10)])
            
            historial_table = ft.DataTable(columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Turno", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario Cierre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ventas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Gastos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Balance", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ], rows=[])
            
            for caja_hist in historial:
                # (idCaja, FechaCaja, Turno, Estado, UsuarioApertura, UsuarioCierre, FechaHoraApertura, FechaHoraCierre, TotalVentas, TotalGastos, BalanceNeto)
                fecha = caja_hist[1].strftime("%Y-%m-%d") if caja_hist[1] else ""
                balance_val = float(caja_hist[10]) if caja_hist[10] else 0.0
                balance_color = self.colors["success"] if balance_val >= 0 else self.colors["danger"]
                id_caja = caja_hist[0]  # idCaja
                
                historial_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(fecha)),
                    ft.DataCell(ft.Text(caja_hist[2] or "")),  # Turno
                    ft.DataCell(ft.Text(caja_hist[5] or "")),  # UsuarioCierre
                    ft.DataCell(ft.Text(f"${float(caja_hist[8] or 0):,.2f}")),  # TotalVentas
                    ft.DataCell(ft.Text(f"${float(caja_hist[9] or 0):,.2f}")),  # TotalGastos
                    ft.DataCell(ft.Text(f"${balance_val:,.2f}", color=balance_color)),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_color=self.colors["primary"],
                        tooltip="Ver detalles de la caja",
                        on_click=lambda e, caja_id=id_caja, fecha_caja=fecha: self.ver_detalles_caja(caja_id, fecha_caja)
                    )),
                ]))
            
            content_parts.append(ft.Container(
                content=ft.Column([historial_table], scroll=ft.ScrollMode.AUTO),
                border=ft.border.all(1, self.colors["border"]), border_radius=8,
                padding=15, bgcolor=self.colors["card"]))
        
        self.content_area.content = ft.Column(content_parts, scroll=ft.ScrollMode.AUTO)
        self.page.update()

    def abrir_caja_action(self):
        turno_field = ft.Dropdown(label="Turno", width=400, value="General",
            options=[ft.dropdown.Option("Mañana", "Mañana"), ft.dropdown.Option("Tarde", "Tarde"),
                    ft.dropdown.Option("Noche", "Noche"), ft.dropdown.Option("General", "General")])
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def confirm_abrir(_):
            success, msg = abrir_caja(self.user_data['id'], turno_field.value or "General")
            self.show_snackbar(msg, not success)
            close_overlay()
            if success: self.show_caja()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCK_OPEN, color=self.colors["success"], size=40),
                    ft.Container(width=15),
                    ft.Text("Abrir Caja", size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                ft.Text("¿En qué turno desea abrir la caja?", size=16),
                ft.Container(height=15),
                turno_field,
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Abrir Caja", on_click=confirm_abrir,
                                    bgcolor=self.colors["success"], color="white", icon=ft.Icons.LOCK_OPEN)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=450, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["success"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def pausar_caja_action(self):
        success, msg = pausar_caja()
        self.show_snackbar(msg, not success)
        if success: self.show_caja()

    def reanudar_caja_action(self):
        success, msg = reanudar_caja()
        self.show_snackbar(msg, not success)
        if success: self.show_caja()

    def cerrar_caja_action(self):
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def confirm_close(_):
            # Primero realizar el cierre formal (registro en CierresDeCaja)
            success_formal, msg_formal = perform_cierre_caja(self.user_data['id'])
            if not success_formal:
                self.show_snackbar(f"❌ Error en cierre formal: {msg_formal}", error=True)
                close_overlay()
                return
            
            # Si el cierre formal fue exitoso, cerrar la caja operativa
            success_caja, msg_caja = cerrar_caja(self.user_data['id'])
            if success_caja:
                self.show_snackbar(f"✓ {msg_formal}", error=False)
                self.show_snackbar(f"✓ {msg_caja}", error=False)
            else:
                self.show_snackbar(f"⚠️ Cierre formal OK pero error en caja: {msg_caja}", error=True)
            
            close_overlay()
            self.show_caja()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCK, color=self.colors["danger"], size=40),
                    ft.Container(width=15),
                    ft.Text("Confirmar Cierre de Caja", size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                ft.Text("¿Está seguro de cerrar la caja?", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Esta acción es permanente y solo se puede hacer una vez al día.", 
                       size=14, color=self.colors["text_secondary"], italic=True),
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Cerrar Caja", on_click=confirm_close,
                                    bgcolor=self.colors["danger"], color="white", icon=ft.Icons.LOCK)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=500, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["danger"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def ver_detalles_caja(self, id_caja, fecha_caja):
        """Muestra una ventana modal con las ventas y productos de una caja específica"""
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        # Obtener las ventas de esta caja
        ventas, err_ventas = get_ventas_de_caja(id_caja)
        
        if err_ventas:
            self.show_snackbar(f"❌ Error al obtener ventas: {err_ventas}", error=True)
            return
        
        if not ventas:
            self.show_snackbar("ℹ️ Esta caja no tiene ventas registradas", error=False)
            return
        
        # Crear una lista de expansión panels, uno por cada venta
        ventas_panels = []
        
        for venta in ventas:
            # venta: (idVenta, FechaVenta, Usuario, Total, MetodoPago)
            id_venta = venta[0]
            fecha_venta = venta[1].strftime("%Y-%m-%d %H:%M:%S") if venta[1] else ""
            usuario = venta[2] or "N/A"
            total = float(venta[3]) if venta[3] else 0.0
            metodo_pago = venta[4] or "N/A"
            
            # Obtener el detalle de productos de esta venta
            productos, err_productos = get_detalle_venta(id_venta)
            
            # Crear tabla de productos
            if productos and not err_productos:
                productos_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Precio Unit.", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Subtotal", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=[]
                )
                
                for prod in productos:
                    # prod: (NombreProducto, Cantidad, PrecioUnitario, Subtotal)
                    productos_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(prod[0] or "N/A")),
                        ft.DataCell(ft.Text(str(prod[1] or 0))),
                        ft.DataCell(ft.Text(f"${float(prod[2] or 0):,.2f}")),
                        ft.DataCell(ft.Text(f"${float(prod[3] or 0):,.2f}")),
                    ]))
                
                productos_content = ft.Container(
                    content=ft.Column([productos_table], scroll=ft.ScrollMode.AUTO),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    border_radius=5
                )
            else:
                productos_content = ft.Text("No se encontraron productos", 
                                          color=self.colors["text_secondary"], 
                                          italic=True)
            
            # Crear el panel expansible para esta venta
            venta_panel = ft.ExpansionPanel(
                header=ft.ListTile(
                    title=ft.Text(f"Venta #{id_venta} - {fecha_venta}", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Usuario: {usuario} | Método: {metodo_pago} | Total: ${total:,.2f}"),
                ),
                content=ft.Container(
                    content=productos_content,
                    padding=ft.padding.only(left=15, right=15, bottom=15)
                ),
                can_tap_header=True,
            )
            
            ventas_panels.append(venta_panel)
        
        # Crear el panel de expansión
        expansion_panel_list = ft.ExpansionPanelList(
            controls=ventas_panels,
            expand_icon_color=self.colors["primary"],
            elevation=0,
        )
        
        # Crear el contenido del diálogo
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT_LONG, color=self.colors["primary"], size=35),
                    ft.Container(width=10),
                    ft.Text(f"Detalles de Caja - {fecha_caja}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay, icon_size=20)
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                ft.Text(f"Total de ventas: {len(ventas)}", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([expansion_panel_list], scroll=ft.ScrollMode.AUTO),
                    height=500,
                    border=ft.border.all(1, self.colors["border"]),
                    border_radius=8,
                    padding=10,
                ),
            ], tight=True),
            width=800,
            bgcolor=self.colors["card"],
            padding=30,
            border_radius=12,
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, 
                              color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        
        self.overlay_dialog = ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True
        )
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def show_usuarios(self):
        usuarios, error = get_all_users()
        if error: self.show_snackbar(f"❌ Error: {error}", error=True); usuarios = []
        
        new_btn = ft.ElevatedButton("➕ Nuevo Usuario", icon=ft.Icons.ADD,
                                   on_click=lambda _: self.new_usuario_dialog(),
                                   bgcolor=self.colors["success"], color="white")
        
        usuarios_table = ft.DataTable(columns=[
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ], rows=[])
        
        for user in usuarios:
            usuarios_table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(user[1])), ft.DataCell(ft.Text(user[2])), ft.DataCell(ft.Text(user[3])),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color=self.colors["info"], 
                                 tooltip="Editar", on_click=lambda _, u=user: self.edit_usuario_dialog(u)),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=self.colors["danger"], 
                                 tooltip="Eliminar", on_click=lambda _, u=user: self.delete_usuario_confirm(u)),
                ], spacing=5)),
            ]))
        
        self.content_area.content = ft.Column([
            ft.Row([ft.Text("Gestión de Usuarios", size=28, weight=ft.FontWeight.BOLD), new_btn], 
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            ft.Container(content=ft.Column([usuarios_table], scroll=ft.ScrollMode.AUTO),
                       border=ft.border.all(1, self.colors["border"]), border_radius=8,
                       padding=15, bgcolor=self.colors["card"]),
        ], scroll=ft.ScrollMode.AUTO)
        self.page.update()

    def new_usuario_dialog(self):
        roles, _ = get_all_roles()
        username_field = ft.TextField(label="Usuario *", width=400)
        nombre_field = ft.TextField(label="Nombre Completo *", width=400)
        password_field = ft.TextField(label="Contraseña *", width=400, password=True, can_reveal_password=True)
        rol_dropdown = ft.Dropdown(label="Rol *", width=400,
            options=[ft.dropdown.Option(str(r[0]), r[1]) for r in roles] if roles else [])
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def save_usuario(_):
            success, msg = create_user(username_field.value, password_field.value,
                nombre_field.value, int(rol_dropdown.value) if rol_dropdown.value else None)
            self.show_snackbar(msg, not success)
            if success: close_overlay(); self.show_usuarios()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("➕ Nuevo Usuario", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay, icon_size=20)
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                username_field, nombre_field, password_field, rol_dropdown,
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", on_click=save_usuario,
                                    bgcolor=self.colors["success"], color="white")
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=500, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["border"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def edit_usuario_dialog(self, usuario):
        roles, _ = get_all_roles()
        username_field = ft.TextField(label="Usuario *", width=400, value=usuario[1])
        nombre_field = ft.TextField(label="Nombre Completo *", width=400, value=usuario[2])
        password_field = ft.TextField(label="Nueva Contraseña (opcional)", width=400, password=True, can_reveal_password=True)
        rol_dropdown = ft.Dropdown(label="Rol *", width=400,
            options=[ft.dropdown.Option(str(r[0]), r[1]) for r in roles] if roles else [])
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def save_changes(_):
            success, msg = update_user(usuario[0], username_field.value, nombre_field.value,
                int(rol_dropdown.value) if rol_dropdown.value else None,
                password_field.value if password_field.value else None)
            self.show_snackbar(msg, not success)
            if success: close_overlay(); self.show_usuarios()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"✏️ Editar: {usuario[1]}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay, icon_size=20)
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                username_field, nombre_field, password_field, rol_dropdown,
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", on_click=save_changes,
                                    bgcolor=self.colors["info"], color="white")
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=500, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["border"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def delete_usuario_confirm(self, usuario):
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def confirm_delete(_):
            success, msg = delete_user(usuario[0])
            self.show_snackbar(msg, not success)
            if success: close_overlay(); self.show_usuarios()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=self.colors["danger"], size=40),
                    ft.Container(width=15),
                    ft.Text("Confirmar Inactivación", size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                ft.Text(f"¿Estás seguro de inactivar el usuario '{usuario[1]}'?", size=16),
                ft.Text("El usuario no podrá iniciar sesión.", size=12, color=self.colors["text_secondary"], italic=True),
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Inactivar", on_click=confirm_delete,
                                    bgcolor=self.colors["danger"], color="white", icon=ft.Icons.BLOCK)
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=450, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["danger"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def show_gastos(self):
        # Formulario lateral mejorado
        self.gasto_desc_field = ft.TextField(
            label="Descripción *", 
            width=380,
            height=55,
            hint_text="Ej: Pago de alquiler",
            max_length=200,
            border_radius=12,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
        )
        
        self.gasto_monto_field = ft.TextField(
            label="Monto *", 
            width=380,
            height=55,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_text="$ ", 
            hint_text="0.00",
            border_radius=12,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
        )
        
        self.gasto_cat_dropdown = ft.Dropdown(
            label="Categoría *", 
            width=380,
            hint_text="Seleccionar categoría",
            border_radius=12,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
            options=[
                ft.dropdown.Option("Servicios"),
                ft.dropdown.Option("Suministros"),
                ft.dropdown.Option("Marketing"),
                ft.dropdown.Option("Mantenimiento"),
                ft.dropdown.Option("Salarios"),
                ft.dropdown.Option("Impuestos"),
                ft.dropdown.Option("Otros"),
            ]
        )
        
        self.gasto_nota_field = ft.TextField(
            label="Nota (opcional)", 
            width=380,
            height=80,
            hint_text="Información adicional...",
            multiline=True,
            max_lines=3,
            border_radius=12,
            border_color=self.colors["border"],
            focused_border_color=self.colors["primary"],
        )
        
        registrar_btn = ft.ElevatedButton(
            "Registrar Gasto",
            icon=ft.Icons.ADD_ROUNDED,
            on_click=lambda _: self.add_gasto_action(),
            bgcolor=self.colors["danger"],
            color="white",
            width=380,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            )
        )
        
        form_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, color=self.colors["danger"], size=28),
                    ft.Container(width=10),
                    ft.Text("Registrar Nuevo Gasto", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                ]),
                ft.Divider(height=20, color=self.colors["border_light"]),
                ft.Text("Complete todos los campos marcados con *", size=12, color=self.colors["text_muted"], italic=True),
                ft.Container(height=15),
                self.gasto_desc_field,
                ft.Container(height=12),
                self.gasto_monto_field,
                ft.Container(height=12),
                self.gasto_cat_dropdown,
                ft.Container(height=12),
                self.gasto_nota_field,
                ft.Container(height=20),
                registrar_btn,
            ], spacing=0),
            bgcolor=self.colors["card"],
            padding=30,
            border_radius=16,
            border=ft.border.all(1, self.colors["border_light"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 2)),
            width=440
        )
        
        # Lista de últimos gastos
        self.gastos_list_view = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        self.refresh_gastos_list()
        
        list_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Últimos Gastos Registrados", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                        ft.Text("Historial de egresos del negocio", size=13, color=self.colors["text_muted"]),
                    ], spacing=5),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.REFRESH_ROUNDED, 
                            tooltip="Refrescar lista",
                            on_click=lambda _: self.refresh_gastos_list(),
                            icon_color=self.colors["primary"],
                            icon_size=24
                        ),
                        bgcolor=self.colors["primary_light"] + "20",
                        border_radius=10,
                    ),
                ]),
                ft.Container(height=10),
                self.gastos_list_view,
            ], spacing=0),
            bgcolor=self.colors["card"],
            padding=30,
            border_radius=16,
            border=ft.border.all(1, self.colors["border_light"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 2)),
            expand=True
        )
        
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Gestión de Gastos", size=32, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                        ft.Text("Registra y controla los egresos del negocio", size=15, color=self.colors["text_muted"]),
                    ], spacing=5),
                ]),
                ft.Container(height=25),
                ft.Row([
                    form_panel,
                    ft.Container(width=25),
                    list_panel,
                ], expand=True, alignment=ft.MainAxisAlignment.START),
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            alignment=ft.alignment.top_center,
            expand=True,
        )
        self.page.update()
    
    def refresh_gastos_list(self):
        gastos = get_all_gastos()
        self.gastos_list_view.controls.clear()
        
        if not gastos:
            self.gastos_list_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.RECEIPT_ROUNDED, size=60, color=self.colors["text_muted"] + "50"),
                        ft.Container(height=10),
                        ft.Text("No hay gastos registrados", size=16, color=self.colors["text_muted"]),
                        ft.Text("Los gastos aparecerán aquí", size=13, color=self.colors["text_muted"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=60
                )
            )
        else:
            for gasto in gastos[:30]:  # Últimos 30
                fecha_str = gasto['fecha'].strftime('%d/%m/%Y') if gasto['fecha'] else ""
                categoria = gasto.get('categoria') or 'Otros'
                nota = gasto.get('nota', '')
                
                # Color por categoría
                cat_colors = {
                    'Servicios': self.colors["info"],
                    'Suministros': self.colors["warning"],
                    'Marketing': self.colors["primary"],
                    'Mantenimiento': self.colors["info"],
                    'Salarios': self.colors["success"],
                    'Impuestos': self.colors["danger"],
                    'Otros': self.colors["text_secondary"]
                }
                cat_color = cat_colors.get(categoria, self.colors["text_secondary"])
                
                # Crear función para eliminar con closure
                def make_delete_handler(gasto_id):
                    def handler(e):
                        self.delete_gasto_action(gasto_id)
                    return handler
                
                self.gastos_list_view.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, color="white", size=22),
                                bgcolor=self.colors["danger"],
                                border_radius=10,
                                padding=12,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(width=15),
                            ft.Column([
                                ft.Text(gasto['descripcion'], weight=ft.FontWeight.W_500, size=14, color=self.colors["text_primary"]),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(categoria, size=11, color=cat_color),
                                        bgcolor=cat_color + "20",
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=6,
                                    ),
                                    ft.Text(f"• {fecha_str}", size=12, color=self.colors["text_muted"]),
                                ], spacing=8),
                                ft.Text(nota, size=12, color=self.colors["text_muted"], italic=True) if nota else ft.Container(),
                            ], spacing=5, expand=True),
                            ft.Column([
                                ft.Text(f"${gasto['monto']:,.2f}", 
                                       weight=ft.FontWeight.BOLD, 
                                       size=16,
                                       color=self.colors["danger"]),
                                ft.Container(
                                    content=ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                        icon_color=self.colors["danger"],
                                        icon_size=20,
                                        tooltip="Eliminar gasto",
                                        on_click=make_delete_handler(gasto.get('id'))
                                    ),
                                    bgcolor=self.colors["danger_light"],
                                    border_radius=8,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=5),
                        ], alignment=ft.MainAxisAlignment.START),
                        padding=18,
                        border=ft.border.all(1, self.colors["border_light"]),
                        border_radius=12,
                        bgcolor=self.colors["card"],
                        ink=True,
                        on_hover=lambda e: setattr(e.control, 'bgcolor', self.colors["bg"] if e.data == "true" else self.colors["card"]) or self.page.update(),
                    )
                )
        
        self.page.update()
    
    def add_gasto_action(self):
        descripcion = self.gasto_desc_field.value.strip() if self.gasto_desc_field.value else ""
        monto_str = self.gasto_monto_field.value.strip() if self.gasto_monto_field.value else ""
        categoria = self.gasto_cat_dropdown.value
        nota = self.gasto_nota_field.value.strip() if self.gasto_nota_field.value else ""
        
        # Validaciones
        if not descripcion:
            self.show_snackbar("⚠️ Ingrese una descripción", error=True)
            return
        
        if len(descripcion) > 200:
            self.show_snackbar("⚠️ La descripción no puede exceder 200 caracteres", error=True)
            return
        
        if not monto_str:
            self.show_snackbar("⚠️ Ingrese el monto", error=True)
            return
        
        if not categoria:
            self.show_snackbar("⚠️ Seleccione una categoría", error=True)
            return
        
        try:
            monto = float(monto_str.replace('$', '').replace(',', '').strip())
            if monto <= 0:
                self.show_snackbar("⚠️ El monto debe ser mayor a 0", error=True)
                return
        except ValueError:
            self.show_snackbar("⚠️ Ingrese un monto válido", error=True)
            return
        
        # Registrar gasto
        success, msg = create_gasto(descripcion, monto, categoria, nota)
        
        if success:
            self.show_snackbar(f"✅ {msg}")
            # Limpiar formulario
            self.gasto_desc_field.value = ""
            self.gasto_monto_field.value = ""
            self.gasto_cat_dropdown.value = None
            self.gasto_nota_field.value = ""
            self.page.update()
            # Refrescar lista
            self.refresh_gastos_list()
        else:
            self.show_snackbar(f"❌ {msg}", error=True)
    
    def delete_gasto_action(self, gasto_id):
        if not gasto_id:
            return
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def confirm_delete(e):
            success, msg = delete_gasto(gasto_id)
            if success:
                self.show_snackbar(f"✅ {msg}")
                close_overlay()
                self.refresh_gastos_list()
            else:
                self.show_snackbar(f"❌ {msg}", error=True)
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING_ROUNDED, color=self.colors["warning"], size=32),
                    ft.Container(width=12),
                    ft.Text("Eliminar Gasto", size=24, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, on_click=close_overlay, icon_size=24)
                ]),
                ft.Divider(height=20, color=self.colors["border_light"]),
                ft.Container(height=10),
                ft.Text("¿Está seguro de eliminar este gasto?", size=16, color=self.colors["text_primary"]),
                ft.Text("Esta acción no se puede deshacer.", size=14, color=self.colors["text_muted"]),
                ft.Container(height=25),
                ft.Row([
                    ft.OutlinedButton(
                        "Cancelar",
                        on_click=close_overlay,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        height=45,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_ROUNDED,
                        on_click=confirm_delete,
                        bgcolor=self.colors["danger"],
                        color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        height=45,
                    ),
                ]),
            ], tight=True),
            width=500,
            bgcolor=self.colors["card"],
            padding=35,
            border_radius=16,
            border=ft.border.all(1, self.colors["border_light"]),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=30, color="#00000020", offset=ft.Offset(0, 10))
        )
        
        self.overlay_dialog = ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
        )
        
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()
    
    def add_gasto_action_old(self):
        desc = self.gasto_desc_field.value.strip() if self.gasto_desc_field.value else ""
        
        if not desc:
            self.show_snackbar("⚠️ Complete la descripción", error=True)
            return
        
        try:
            monto_val = float(self.gasto_monto_field.value) if self.gasto_monto_field.value else 0
            if monto_val <= 0:
                self.show_snackbar("⚠️ El monto debe ser mayor a 0", error=True)
                return
            
            categoria = self.gasto_cat_dropdown.value or 'Otros'
            success, msg = create_gasto(desc, monto_val, categoria)
            
            if success:
                self.show_snackbar(f"✅ {msg}")
                # Limpiar formulario
                self.gasto_desc_field.value = ""
                self.gasto_monto_field.value = ""
                self.gasto_cat_dropdown.value = None
                self.refresh_gastos_list()
            else:
                self.show_snackbar(f"❌ {msg}", error=True)
        except ValueError:
            self.show_snackbar("⚠️ El monto debe ser un número válido", error=True)
        except Exception as e:
            self.show_snackbar(f"❌ Error: {str(e)}", error=True)

    def show_metodos_pago(self):
        metodos = get_all_metodos_pago()
        new_btn = ft.ElevatedButton("➕ Nuevo Método", icon=ft.Icons.ADD,
                                   on_click=lambda _: self.new_metodo_dialog(),
                                   bgcolor=self.colors["success"], color="white")
        metodos_table = ft.DataTable(columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ], rows=[])
        for metodo in metodos:
            # Estado con color
            if metodo['activo']:
                estado_widget = ft.Text("Activo", color="#10B981", weight=ft.FontWeight.BOLD)
            else:
                estado_widget = ft.Text("Inactivo", color="#F87171", weight=ft.FontWeight.BOLD)
            
            metodos_table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(metodo['nombre'])),
                ft.DataCell(ft.Text(metodo['tipo'])),
                ft.DataCell(estado_widget),
                ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color=self.colors["info"], 
                                 tooltip="Editar", on_click=lambda _, m=metodo: self.edit_metodo_dialog(m)),
                ], spacing=5)),
            ]))
        self.content_area.content = ft.Column([
            ft.Row([ft.Text("Métodos de Pago", size=28, weight=ft.FontWeight.BOLD), new_btn], 
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            ft.Container(content=metodos_table, border=ft.border.all(1, self.colors["border"]),
                       border_radius=8, padding=15, bgcolor=self.colors["card"]),
        ], scroll=ft.ScrollMode.AUTO)
        self.page.update()

    def new_metodo_dialog(self):
        nombre_field = ft.TextField(label="Nombre *", width=400)
        tipo_dropdown = ft.Dropdown(label="Tipo *", width=400, value="Efectivo", options=[
                ft.dropdown.Option("Efectivo", "Efectivo"), ft.dropdown.Option("Tarjeta", "Tarjeta"),
                ft.dropdown.Option("Transferencia", "Transferencia"), ft.dropdown.Option("Otro", "Otro")])
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def save_metodo(_):
            success, msg = create_metodo_pago(nombre_field.value, tipo_dropdown.value or 'Efectivo')
            self.show_snackbar(msg, not success)
            if success: close_overlay(); self.show_metodos_pago()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("➕ Nuevo Método de Pago", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay, icon_size=20)
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                nombre_field, tipo_dropdown,
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", on_click=save_metodo,
                                    bgcolor=self.colors["success"], color="white")
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=500, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["border"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def edit_metodo_dialog(self, metodo):
        nombre_field = ft.TextField(label="Nombre *", width=400, value=metodo['nombre'])
        tipo_dropdown = ft.Dropdown(label="Tipo *", width=400, value=metodo['tipo'], options=[
                ft.dropdown.Option("Efectivo", "Efectivo"), ft.dropdown.Option("Tarjeta", "Tarjeta"),
                ft.dropdown.Option("Transferencia", "Transferencia"), ft.dropdown.Option("Otro", "Otro")])
        activo_switch = ft.Switch(label="Activo", value=metodo['activo'])
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        def save_changes(_):
            success, msg = update_metodo_pago(metodo['id'], nombre_field.value, 
                                             tipo_dropdown.value, activo_switch.value)
            self.show_snackbar(msg, not success)
            if success: close_overlay(); self.show_metodos_pago()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"✏️ Editar: {metodo['nombre']}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_overlay, icon_size=20)
                ]),
                ft.Divider(height=20, color=self.colors["border"]),
                nombre_field, tipo_dropdown, activo_switch,
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", on_click=save_changes,
                                    bgcolor=self.colors["info"], color="white")
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            width=500, bgcolor=self.colors["card"], padding=30, border_radius=12,
            border=ft.border.all(2, self.colors["border"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        )
        self.overlay_dialog = ft.Container(content=dialog_content, alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), expand=True)
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()

    def delete_metodo_confirm(self, metodo):
        def confirm_delete(_):
            success, msg = delete_metodo_pago(metodo['id'])
            self.show_snackbar(msg, not success)
            if success: self.close_dialog(dialog); self.show_metodos_pago()
        dialog = ft.AlertDialog(title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Eliminar el método '{metodo['nombre']}'?"),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog)),
                    ft.ElevatedButton("Eliminar", on_click=confirm_delete, 
                                    bgcolor=self.colors["danger"], color="white")])
        self.page.dialog = dialog; dialog.open = True; self.page.update()

    def show_reportes(self):
        """Muestra reportes mensuales con cierres de caja agrupados por mes"""
        from app.caja_logic import get_historial_cierres
        from datetime import datetime, timedelta
        
        # Inicializar fechas de filtro si no existen
        if not hasattr(self, 'fecha_desde_reportes'):
            self.fecha_desde_reportes = None
        if not hasattr(self, 'fecha_hasta_reportes'):
            self.fecha_hasta_reportes = None
        
        historial_cierres, err = get_historial_cierres()
        
        if err or not historial_cierres:
            self.content_area.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=64, color=self.colors["text_secondary"]),
                    ft.Container(height=20),
                    ft.Text("📊 Reportes Mensuales", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text("No hay cierres de caja registrados" if not err else f"Error: {err}",
                           color=self.colors["text_secondary"], size=16)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
            self.page.update()
            return
        
        # Aplicar filtro de fechas si están definidas
        if self.fecha_desde_reportes or self.fecha_hasta_reportes:
            historial_filtrado = []
            for cierre in historial_cierres:
                fecha_cierre = cierre[0]
                if fecha_cierre:
                    fecha_solo = fecha_cierre.date() if hasattr(fecha_cierre, 'date') else fecha_cierre
                    incluir = True
                    if self.fecha_desde_reportes and fecha_solo < self.fecha_desde_reportes:
                        incluir = False
                    if self.fecha_hasta_reportes and fecha_solo > self.fecha_hasta_reportes:
                        incluir = False
                    if incluir:
                        historial_filtrado.append(cierre)
            historial_cierres = historial_filtrado
        
        # Agrupar cierres por mes/año
        cierres_por_mes = {}
        for cierre in historial_cierres:
            fecha_cierre = cierre[0]  # FechaCierre
            if fecha_cierre:
                mes_año = fecha_cierre.strftime("%Y-%m")
                mes_nombre = fecha_cierre.strftime("%B %Y")
                
                if mes_año not in cierres_por_mes:
                    cierres_por_mes[mes_año] = {
                        'nombre': mes_nombre,
                        'cierres': [],
                        'total_ventas': 0,
                        'total_gastos': 0,
                        'total_balance': 0
                    }
                
                cierres_por_mes[mes_año]['cierres'].append(cierre)
                cierres_por_mes[mes_año]['total_ventas'] += float(cierre[2]) if cierre[2] else 0
                cierres_por_mes[mes_año]['total_gastos'] += float(cierre[3]) if cierre[3] else 0
                cierres_por_mes[mes_año]['total_balance'] += float(cierre[4]) if cierre[4] else 0
        
        # Traducir meses al español
        meses_es = {
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
            'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
            'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
            'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        
        # Crear acordeones por mes
        meses_column = ft.Column([], spacing=15)
        
        for mes_año in sorted(cierres_por_mes.keys(), reverse=True):
            mes_data = cierres_por_mes[mes_año]
            mes_nombre = mes_data['nombre']
            for en, es in meses_es.items():
                mes_nombre = mes_nombre.replace(en, es)
            
            balance_color = self.colors["success"] if mes_data['total_balance'] >= 0 else self.colors["danger"]
            
            # Crear tabla de cierres del mes
            cierres_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(ft.Text("Ventas", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(ft.Text("Gastos", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(ft.Text("Balance", weight=ft.FontWeight.BOLD, size=13)),
                    ft.DataColumn(ft.Text("Detalle", weight=ft.FontWeight.BOLD, size=13)),
                ],
                rows=[],
                border=ft.border.all(1, self.colors["border"]),
                border_radius=8,
                horizontal_lines=ft.BorderSide(1, self.colors["border_light"]),
            )
            
            for cierre in mes_data['cierres']:
                fecha_cierre_obj = cierre[0]  # Guardar el objeto datetime original
                fecha_cierre = cierre[0].strftime("%d/%m/%Y") if cierre[0] else ""
                nombre_usuario = cierre[1] or ""
                ventas = float(cierre[2]) if cierre[2] else 0.0
                gastos = float(cierre[3]) if cierre[3] else 0.0
                balance = float(cierre[4]) if cierre[4] else 0.0
                bal_color = self.colors["success"] if balance >= 0 else self.colors["danger"]
                
                # Crear función para manejar el click con el scope correcto
                def make_detalle_click(fecha_obj):
                    def handler(e):
                        try:
                            self.show_detalle_cierre_productos(fecha_obj)
                        except Exception as ex:
                            self.show_snackbar(f"❌ Error: {str(ex)}", error=True)
                    return handler
                
                cierres_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(fecha_cierre, size=12)),
                    ft.DataCell(ft.Text(nombre_usuario, size=12)),
                    ft.DataCell(ft.Text(f"${ventas:,.2f}", size=12, color=self.colors["success"])),
                    ft.DataCell(ft.Text(f"${gastos:,.2f}", size=12, color=self.colors["danger"])),
                    ft.DataCell(ft.Text(f"${balance:,.2f}", size=12, color=bal_color, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_size=18,
                        icon_color=self.colors["primary"],
                        tooltip="Ver productos vendidos",
                        on_click=make_detalle_click(fecha_cierre_obj)
                    )),
                ]))
            
            # Contenedor expandible
            detalle_container = ft.Container(
                content=ft.Column([
                    ft.Container(height=10),
                    ft.Container(
                        content=cierres_table,
                        padding=15,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=8,
                    ),
                ]),
                visible=False,
            )
            
            def make_toggle(container):
                def toggle(e):
                    container.visible = not container.visible
                    e.control.icon = ft.Icons.EXPAND_LESS if container.visible else ft.Icons.EXPAND_MORE
                    self.page.update()
                return toggle
            
            expand_btn = ft.IconButton(
                icon=ft.Icons.EXPAND_MORE,
                icon_color=self.colors["primary"],
                on_click=make_toggle(detalle_container)
            )
            
            mes_card = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH, color=self.colors["primary"], size=28),
                            ft.Container(width=15),
                            ft.Column([
                                ft.Text(mes_nombre, size=20, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{len(mes_data['cierres'])} cierres registrados", 
                                       size=13, color=self.colors["text_secondary"]),
                            ], spacing=2, expand=True),
                            ft.Column([
                                ft.Text(f"${mes_data['total_ventas']:,.2f}", 
                                       size=16, weight=ft.FontWeight.BOLD, color=self.colors["success"]),
                                ft.Text("Ventas", size=12, color=self.colors["text_secondary"]),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END),
                            ft.Container(width=20),
                            ft.Column([
                                ft.Text(f"${mes_data['total_balance']:,.2f}", 
                                       size=16, weight=ft.FontWeight.BOLD, color=balance_color),
                                ft.Text("Balance", size=12, color=self.colors["text_secondary"]),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END),
                            ft.Container(width=15),
                            expand_btn,
                        ]),
                        padding=20,
                        ink=True,
                        on_click=make_toggle(detalle_container),
                    ),
                    detalle_container,
                ]),
                bgcolor=self.colors["card"],
                border_radius=12,
                border=ft.border.all(1, self.colors["border"]),
            )
            
            meses_column.controls.append(mes_card)
        
        # Crear campos de filtro por fecha
        def format_date_input(e, field):
            """Auto-formatea la fecha mientras se escribe"""
            val = field.value.replace("/", "")
            if len(val) > 8:
                val = val[:8]
            
            formatted = ""
            for i, char in enumerate(val):
                if char.isdigit():
                    formatted += char
                    if i == 1 or i == 3:
                        formatted += "/"
            
            field.value = formatted
            field.update()
        
        fecha_desde_field = ft.TextField(
            label="Desde",
            hint_text="DD/MM/AAAA",
            width=150,
            height=50,
            value=self.fecha_desde_reportes.strftime("%d/%m/%Y") if self.fecha_desde_reportes else "",
            text_size=14,
        )
        fecha_desde_field.on_change = lambda e: format_date_input(e, fecha_desde_field)
        
        fecha_hasta_field = ft.TextField(
            label="Hasta",
            hint_text="DD/MM/AAAA",
            width=150,
            height=50,
            value=self.fecha_hasta_reportes.strftime("%d/%m/%Y") if self.fecha_hasta_reportes else "",
            text_size=14,
        )
        fecha_hasta_field.on_change = lambda e: format_date_input(e, fecha_hasta_field)
        
        def aplicar_filtro(e):
            try:
                # Parsear fechas desde los campos
                if fecha_desde_field.value:
                    self.fecha_desde_reportes = datetime.strptime(fecha_desde_field.value, "%d/%m/%Y").date()
                else:
                    self.fecha_desde_reportes = None
                    
                if fecha_hasta_field.value:
                    self.fecha_hasta_reportes = datetime.strptime(fecha_hasta_field.value, "%d/%m/%Y").date()
                else:
                    self.fecha_hasta_reportes = None
                
                # Recargar reportes con filtro
                self.show_reportes()
            except ValueError:
                self.show_snackbar("❌ Formato de fecha inválido. Use DD/MM/AAAA", error=True)
        
        def limpiar_filtro(e):
            self.fecha_desde_reportes = None
            self.fecha_hasta_reportes = None
            fecha_desde_field.value = ""
            fecha_hasta_field.value = ""
            self.show_reportes()
        
        filtros_row = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, color=self.colors["primary"], size=24),
                ft.Container(width=10),
                fecha_desde_field,
                ft.Container(width=10),
                fecha_hasta_field,
                ft.Container(width=15),
                ft.ElevatedButton(
                    "Filtrar",
                    icon=ft.Icons.FILTER_ALT,
                    on_click=aplicar_filtro,
                    bgcolor=self.colors["primary"],
                    color="white",
                ),
                ft.Container(width=10),
                ft.OutlinedButton(
                    "Limpiar",
                    icon=ft.Icons.CLEAR,
                    on_click=limpiar_filtro,
                ),
            ], spacing=5),
            bgcolor=self.colors["card"],
            border_radius=10,
            padding=15,
        )
        
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📊 Reportes Mensuales", size=32, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                ]),
                ft.Container(height=15),
                filtros_row,
                ft.Container(height=10),
                meses_column,
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            alignment=ft.alignment.top_left,
            expand=True,
            padding=20,
        )
        self.page.update()
    
    def show_detalle_cierre_productos(self, fecha_cierre):
        """Muestra productos vendidos en un día específico"""
        from app.database import get_connection
        
        # Convertir datetime a date si es necesario
        if hasattr(fecha_cierre, 'date'):
            fecha_solo = fecha_cierre.date()
        else:
            fecha_solo = fecha_cierre
        
        conn = get_connection()
        if not conn:
            self.show_snackbar("❌ Error de conexión", error=True)
            return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.NombreProducto, dv.Cantidad, dv.PrecioUnitario, 
                       (dv.Cantidad * dv.PrecioUnitario) AS Subtotal
                FROM DetalleVentas dv
                INNER JOIN Ventas v ON dv.idVenta = v.idVenta
                INNER JOIN Productos p ON dv.idProducto = p.idProducto
                WHERE CAST(v.FechaVenta AS DATE) = CAST(? AS DATE)
                ORDER BY v.FechaVenta DESC
            """
            try:
                cursor.execute(query, (fecha_solo,))
                productos = cursor.fetchall()
            except Exception as query_error:
                cursor.close()
                conn.close()
                self.show_snackbar(f"❌ Error en consulta: {str(query_error)}", error=True)
                return
            
            cursor.close()
            conn.close()
            
            if not productos:
                self.show_snackbar("ℹ️ No hay productos vendidos ese día", error=False)
                return
            
            tabla_productos = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD, size=14, color=self.colors["text_primary"])),
                    ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD, size=14, color=self.colors["text_primary"])),
                    ft.DataColumn(ft.Text("Precio Unitario", weight=ft.FontWeight.BOLD, size=14, color=self.colors["text_primary"])),
                    ft.DataColumn(ft.Text("Subtotal", weight=ft.FontWeight.BOLD, size=14, color=self.colors["text_primary"])),
                ],
                rows=[],
                border=ft.border.all(2, self.colors["border"]),
                border_radius=10,
                horizontal_lines=ft.BorderSide(1, self.colors["border_light"]),
                heading_row_color=ft.Colors.GREY_100,
                heading_row_height=50,
                data_row_min_height=45,
            )
            
            total_dia = 0
            for prod in productos:
                nombre = prod[0]
                cantidad = prod[1]
                precio = float(prod[2])
                subtotal = float(prod[3])
                total_dia += subtotal
                
                tabla_productos.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(nombre, size=13, color=self.colors["text_primary"])),
                    ft.DataCell(ft.Container(
                        content=ft.Text(str(cantidad), size=14, weight=ft.FontWeight.BOLD, color=self.colors["primary"]),
                        alignment=ft.alignment.center,
                    )),
                    ft.DataCell(ft.Text(f"${precio:,.2f}", size=13, color=self.colors["text_secondary"])),
                    ft.DataCell(ft.Text(f"${subtotal:,.2f}", size=14, weight=ft.FontWeight.BOLD, color=self.colors["success"])),
                ]))
            
            # Formatear la fecha para el título
            fecha_str = fecha_solo.strftime('%d/%m/%Y') if hasattr(fecha_solo, 'strftime') else str(fecha_solo)
            
            # Crear overlay modal similar al formulario de productos
            def cerrar_modal(e):
                self.page.overlay.clear()
                self.page.update()
            
            modal_content = ft.Container(
                content=ft.Column([
                    # Header con gradiente visual
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT_LONG, size=32, color="white"),
                                bgcolor=self.colors["primary"],
                                border_radius=8,
                                padding=8,
                            ),
                            ft.Container(width=15),
                            ft.Column([
                                ft.Text("Detalle de Ventas", size=16, weight=ft.FontWeight.BOLD, color=self.colors["text_primary"]),
                                ft.Text(f"Fecha: {fecha_str}", size=13, color=self.colors["text_secondary"]),
                            ], spacing=2),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=28,
                                icon_color=self.colors["text_secondary"],
                                on_click=cerrar_modal,
                                tooltip="Cerrar (ESC)"
                            ),
                        ]),
                        padding=25,
                        bgcolor=self.colors["card"],
                    ),
                    ft.Divider(height=1, thickness=2, color=self.colors["border"]),
                    
                    # Información de resumen
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INVENTORY_2, size=20, color=self.colors["primary"]),
                            ft.Text(f"Total de productos: {len(productos)}", size=14, weight=ft.FontWeight.W_500, color=self.colors["text_secondary"]),
                        ]),
                        padding=ft.padding.only(left=25, right=25, top=15, bottom=10),
                        bgcolor=ft.Colors.BLUE_50,
                    ),
                    
                    # Tabla de productos con scroll
                    ft.Container(
                        content=ft.Column([tabla_productos], scroll=ft.ScrollMode.AUTO),
                        height=400,
                        padding=25,
                        bgcolor="white",
                    ),
                    
                    # Footer con total destacado
                    ft.Container(
                        content=ft.Column([
                            ft.Divider(height=1, thickness=2, color=self.colors["border"]),
                            ft.Container(height=10),
                            ft.Row([
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.ATTACH_MONEY, size=28, color=self.colors["success"]),
                                        ft.Column([
                                            ft.Text("TOTAL DEL DÍA", size=13, color=self.colors["text_secondary"], weight=ft.FontWeight.W_500),
                                            ft.Text(f"${total_dia:,.2f}", size=28, weight=ft.FontWeight.BOLD, color=self.colors["success"]),
                                        ], spacing=2),
                                    ]),
                                    padding=15,
                                    bgcolor=ft.Colors.GREEN_50,
                                    border_radius=10,
                                    border=ft.border.all(2, self.colors["success"]),
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ], spacing=5),
                        padding=25,
                        bgcolor=self.colors["card"],
                    ),
                    
                    # Botón cerrar
                    ft.Container(
                        content=ft.Row([
                            ft.Container(expand=True),
                            ft.ElevatedButton(
                                "Cerrar",
                                icon=ft.Icons.CHECK_CIRCLE,
                                on_click=cerrar_modal,
                                bgcolor=self.colors["primary"],
                                color="white",
                                height=50,
                                width=200,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                        ]),
                        padding=ft.padding.only(left=25, right=25, bottom=25, top=15),
                    ),
                ], spacing=0, tight=True),
                width=900,
                bgcolor="white",
                border_radius=15,
                shadow=ft.BoxShadow(
                    spread_radius=8,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                    offset=ft.Offset(0, 5),
                ),
            )
            
            overlay = ft.Container(
                content=ft.Stack([
                    # Fondo oscuro
                    ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                        expand=True,
                        on_click=cerrar_modal,
                    ),
                    # Modal centrado
                    ft.Container(
                        content=modal_content,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ]),
                expand=True,
            )
            
            self.page.overlay.append(overlay)
            self.page.update()
            
        except Exception as e:
            self.show_snackbar(f"❌ Error: {str(e)}", error=True)
            if conn:
                conn.close()
    
    def generar_reporte_financiero(self):
        # Esta función ya no se usa, pero la dejamos por compatibilidad
        pass

    def logo_click_handler(self, e):
        """Manejador de clic en el logo - Solo para desarrolladores"""
        if self.user_data.get('rol') != 'Dev':
            return  # Seguridad adicional
        
        # Mostrar diálogo de confirmación para reset
        self.mostrar_dialogo_reset_sistema()
    
    def mostrar_dialogo_reset_sistema(self):
        """Muestra un diálogo de confirmación para resetear completamente el sistema"""
        
        def close_overlay(e=None):
            if hasattr(self, 'overlay_dialog') and self.overlay_dialog in self.page.overlay:
                self.page.overlay.remove(self.overlay_dialog)
                self.page.update()
        
        # Campo de confirmación
        confirmacion_field = ft.TextField(
            label="Escriba 'CONFIRMAR RESET' para continuar",
            width=500,
            border_color=self.colors["danger"],
        )
        
        def ejecutar_reset(e):
            if confirmacion_field.value != "CONFIRMAR RESET":
                self.show_snackbar("⚠️ Debe escribir 'CONFIRMAR RESET' exactamente", error=True)
                return
            
            close_overlay()
            self.reset_sistema_completo()
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING_ROUNDED, color=self.colors["danger"], size=50),
                    ft.Container(width=15),
                    ft.Text("⚠️ RESETEAR SISTEMA COMPLETO", 
                           size=22, 
                           weight=ft.FontWeight.BOLD,
                           color=self.colors["danger"]),
                ]),
                ft.Divider(height=30, color=self.colors["danger"]),
                
                ft.Text("ADVERTENCIA: Esta acción es IRREVERSIBLE", 
                       size=18, 
                       weight=ft.FontWeight.BOLD,
                       color=self.colors["danger"]),
                
                ft.Container(height=15),
                
                ft.Text("Esta operación eliminará:", size=16, weight=ft.FontWeight.BOLD),
                ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=self.colors["danger"]), 
                           ft.Text("  Toda la base de datos de SQL Server", size=15)]),
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=self.colors["danger"]), 
                           ft.Text("  Todas las ventas, productos y usuarios", size=15)]),
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=self.colors["danger"]), 
                           ft.Text("  El archivo de configuración (connection_data.json)", size=15)]),
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=self.colors["danger"]), 
                           ft.Text("  TODO el historial del negocio", size=15)]),
                ], spacing=8),
                
                ft.Container(height=20),
                
                ft.Text("El sistema volverá al estado inicial de configuración.", 
                       size=14, 
                       color=self.colors["text_secondary"],
                       italic=True),
                
                ft.Container(height=25),
                
                confirmacion_field,
                
                ft.Container(height=25),
                
                ft.Row([
                    ft.TextButton("Cancelar", on_click=close_overlay),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "🔴 RESETEAR SISTEMA",
                        on_click=ejecutar_reset,
                        bgcolor=self.colors["danger"],
                        color="white",
                        icon=ft.Icons.DELETE_FOREVER
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=650,
            bgcolor=self.colors["card"],
            padding=35,
            border_radius=12,
            border=ft.border.all(3, self.colors["danger"]),
            shadow=ft.BoxShadow(
                spread_radius=5, 
                blur_radius=20, 
                color=ft.Colors.with_opacity(0.5, ft.Colors.RED)
            )
        )
        
        self.overlay_dialog = ft.Container(
            content=dialog_content,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
            expand=True
        )
        self.page.overlay.append(self.overlay_dialog)
        self.page.update()
    
    def reset_sistema_completo(self):
        """Ejecuta el reset completo del sistema: elimina BD y archivo de configuración"""
        import os
        
        # Mostrar progreso
        progress_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔄 Reseteando sistema...", size=18),
            content=ft.Column([
                ft.ProgressRing(),
                ft.Container(height=15),
                ft.Text("Por favor espere...", size=14)
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        )
        self.page.dialog = progress_dialog
        progress_dialog.open = True
        self.page.update()
        
        try:
            # 1. Eliminar la base de datos
            success_db, msg_db = drop_database()
            if not success_db:
                raise Exception(f"Error al eliminar BD: {msg_db}")
            
            # 2. Eliminar el archivo de configuración JSON
            if os.path.exists(CONNECTION_FILE):
                os.remove(CONNECTION_FILE)
                print(f"✅ Archivo {CONNECTION_FILE} eliminado.")
            
            # 3. Resetear variables globales
            self.user_data = None
            self.current_view = None
            self.config = None
            
            # Cerrar el diálogo de progreso
            progress_dialog.open = False
            self.page.update()
            
            # Mostrar mensaje de éxito
            success_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=self.colors["success"], size=35),
                    ft.Text("  Sistema Reseteado", size=20)
                ]),
                content=ft.Column([
                    ft.Text("El sistema ha sido reseteado completamente.", size=16),
                    ft.Container(height=10),
                    ft.Text("Será redirigido al wizard de configuración inicial.",
                           size=14, color=self.colors["text_secondary"])
                ], tight=True),
                actions=[
                    ft.TextButton("Continuar", 
                                 on_click=lambda _: self.cerrar_dialogo_y_reiniciar())
                ],
            )
            self.page.dialog = success_dialog
            success_dialog.open = True
            self.page.update()
            
        except Exception as e:
            # Cerrar el diálogo de progreso
            progress_dialog.open = False
            self.page.update()
            
            # Mostrar error
            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.ERROR, color=self.colors["danger"], size=35),
                    ft.Text("  Error al resetear", size=20)
                ]),
                content=ft.Text(f"Error: {str(e)}", size=14),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda _: setattr(error_dialog, 'open', False) or self.page.update())
                ],
            )
            self.page.dialog = error_dialog
            error_dialog.open = True
            self.page.update()
            
            print(f"❌ Error durante reset: {e}")
    
    def cerrar_dialogo_y_reiniciar(self):
        """Cierra el diálogo actual y vuelve al wizard de configuración"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
        
        # Volver al wizard de configuración inicial
        print("🔄 Volviendo al wizard de configuración...")
        self.show_setup_wizard()

    def build_reportes_mensuales_view(self):
        """Construye la vista de reportes mensuales con cierres agrupados"""
        from app.caja_logic import get_historial_cierres
        
        historial_cierres, err = get_historial_cierres()
        
        if err or not historial_cierres:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=64, color=self.colors["text_secondary"]),
                    ft.Container(height=10),
                    ft.Text("No hay cierres registrados" if not err else f"Error: {err}",
                           color=self.colors["text_secondary"], size=16)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=50
            )
        
        # Agrupar cierres por mes/año
        cierres_por_mes = {}
        for cierre in historial_cierres:
            fecha_cierre = cierre[0]  # FechaCierre
            if fecha_cierre:
                mes_año = fecha_cierre.strftime("%Y-%m")  # Formato: 2025-11
                mes_nombre = fecha_cierre.strftime("%B %Y")  # Formato: November 2025
                
                if mes_año not in cierres_por_mes:
                    cierres_por_mes[mes_año] = {
                        'nombre': mes_nombre,
                        'cierres': [],
                        'total_ventas': 0,
                        'total_gastos': 0,
                        'total_balance': 0
                    }
                
                cierres_por_mes[mes_año]['cierres'].append(cierre)
                cierres_por_mes[mes_año]['total_ventas'] += float(cierre[2]) if cierre[2] else 0
                cierres_por_mes[mes_año]['total_gastos'] += float(cierre[3]) if cierre[3] else 0
                cierres_por_mes[mes_año]['total_balance'] += float(cierre[4]) if cierre[4] else 0
        
        # Crear acordeón con meses
        meses_column = ft.Column([], spacing=15)
        
        for mes_año in sorted(cierres_por_mes.keys(), reverse=True):
            mes_data = cierres_por_mes[mes_año]
            meses_column.controls.append(
                self.create_mes_accordion(mes_año, mes_data)
            )
        
        return meses_column
    
    def create_mes_accordion(self, mes_año, mes_data):
        """Crea un acordeón expandible para un mes con sus cierres"""
        balance_color = self.colors["success"] if mes_data['total_balance'] >= 0 else self.colors["danger"]
        
        # Traducir nombre del mes al español
        meses_es = {
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
            'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
            'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
            'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        mes_nombre = mes_data['nombre']
        for en, es in meses_es.items():
            mes_nombre = mes_nombre.replace(en, es)
        
        # Contenedor expandible
        detalle_container = ft.Container(
            content=ft.Column([
                ft.Container(height=10),
                self.create_cierres_table(mes_data['cierres']),
            ]),
            visible=False,
        )
        
        def toggle_expand(e):
            detalle_container.visible = not detalle_container.visible
            e.control.icon = ft.Icons.EXPAND_LESS if detalle_container.visible else ft.Icons.EXPAND_MORE
            self.page.update()
        
        return ft.Container(
            content=ft.Column([
                # Header del mes (clickeable)
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_MONTH, color=self.colors["primary"], size=28),
                        ft.Container(width=15),
                        ft.Column([
                            ft.Text(mes_nombre, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{len(mes_data['cierres'])} cierres registrados", 
                                   size=13, color=self.colors["text_secondary"]),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(f"${mes_data['total_ventas']:,.2f}", 
                                   size=16, weight=ft.FontWeight.BOLD, color=self.colors["success"]),
                            ft.Text("Ventas", size=12, color=self.colors["text_secondary"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END),
                        ft.Container(width=20),
                        ft.Column([
                            ft.Text(f"${mes_data['total_balance']:,.2f}", 
                                   size=16, weight=ft.FontWeight.BOLD, color=balance_color),
                            ft.Text("Balance", size=12, color=self.colors["text_secondary"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END),
                        ft.Container(width=15),
                        ft.IconButton(
                            icon=ft.Icons.EXPAND_MORE,
                            on_click=toggle_expand,
                            icon_color=self.colors["primary"],
                        ),
                    ]),
                    padding=20,
                    ink=True,
                    on_click=toggle_expand,
                ),
                # Detalle de cierres (expandible)
                detalle_container,
            ]),
            bgcolor=self.colors["card"],
            border_radius=12,
            border=ft.border.all(1, self.colors["border"]),
        )
    
    def create_cierres_table(self, cierres):
        """Crea tabla con los cierres del mes"""
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ventas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Gastos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Balance", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Detalle", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, self.colors["border"]),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, self.colors["border_light"]),
        )
        
        for cierre in cierres:
            # (FechaCierre, NombreCompleto, TotalVentas, TotalGastos, BalanceNeto)
            fecha_cierre = cierre[0].strftime("%d/%m/%Y") if cierre[0] else ""
            nombre_usuario = cierre[1] or ""
            ventas = float(cierre[2]) if cierre[2] else 0.0
            gastos = float(cierre[3]) if cierre[3] else 0.0
            balance = float(cierre[4]) if cierre[4] else 0.0
            balance_color = self.colors["success"] if balance >= 0 else self.colors["danger"]
            
            # Botón para ver detalle de productos
            ver_detalle_btn = ft.IconButton(
                icon=ft.Icons.VISIBILITY,
                icon_color=self.colors["primary"],
                tooltip="Ver productos vendidos",
                on_click=lambda _, f=cierre[0]: self.show_detalle_cierre(f)
            )
            
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(fecha_cierre)),
                ft.DataCell(ft.Text(nombre_usuario)),
                ft.DataCell(ft.Text(f"${ventas:,.2f}", color=self.colors["success"])),
                ft.DataCell(ft.Text(f"${gastos:,.2f}", color=self.colors["danger"])),
                ft.DataCell(ft.Text(f"${balance:,.2f}", color=balance_color, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ver_detalle_btn),
            ]))
        
        return ft.Container(
            content=tabla,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
        )
    
    def show_detalle_cierre(self, fecha_cierre):
        """Muestra el detalle de productos vendidos en un cierre específico"""
        from app.database import get_connection
        
        # Obtener productos vendidos ese día
        conn = get_connection()
        if not conn:
            self.show_snackbar("❌ Error de conexión", error=True)
            return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.NombreProducto, dv.Cantidad, dv.PrecioUnitario, 
                       (dv.Cantidad * dv.PrecioUnitario) AS Subtotal,
                       v.FechaHoraVenta
                FROM DetallesVentas dv
                INNER JOIN Ventas v ON dv.idVenta = v.idVenta
                INNER JOIN Productos p ON dv.idProducto = p.idProducto
                WHERE CAST(v.FechaHoraVenta AS DATE) = ?
                ORDER BY v.FechaHoraVenta DESC
            """
            cursor.execute(query, (fecha_cierre,))
            productos = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not productos:
                self.show_snackbar("ℹ️ No hay productos vendidos ese día", error=False)
                return
            
            # Crear tabla de productos
            tabla_productos = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Precio Unit.", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Subtotal", weight=ft.FontWeight.BOLD)),
                ],
                rows=[],
            )
            
            total_dia = 0
            for prod in productos:
                nombre = prod[0]
                cantidad = prod[1]
                precio = float(prod[2])
                subtotal = float(prod[3])
                total_dia += subtotal
                
                tabla_productos.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(nombre)),
                    ft.DataCell(ft.Text(str(cantidad))),
                    ft.DataCell(ft.Text(f"${precio:,.2f}")),
                    ft.DataCell(ft.Text(f"${subtotal:,.2f}", weight=ft.FontWeight.BOLD)),
                ]))
            
            # Crear diálogo
            dialog = ft.AlertDialog(
                title=ft.Text(f"Productos Vendidos - {fecha_cierre.strftime('%d/%m/%Y')}"),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=tabla_productos,
                            height=400,
                            border=ft.border.all(1, self.colors["border"]),
                            border_radius=8,
                            padding=10,
                        ),
                        ft.Divider(),
                        ft.Row([
                            ft.Text("TOTAL DEL DÍA:", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"${total_dia:,.2f}", size=18, weight=ft.FontWeight.BOLD, 
                                   color=self.colors["success"]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], tight=True),
                    width=700,
                ),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog()),
                ],
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            
        except Exception as e:
            self.show_snackbar(f"❌ Error: {str(e)}", error=True)
            if conn:
                conn.close()
    
    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def generar_reporte_financiero(self):
        # Esta función ya no se usa, pero la dejamos por compatibilidad
        pass

    def logout(self):
        self.user_data = None; self.current_view = None; self.show_login()

    def show_snackbar(self, message, error=False):
        bg_color = self.colors["danger"] if error else self.colors["success"]
        icon = ft.Icons.ERROR_ROUNDED if error else ft.Icons.CHECK_CIRCLE_ROUNDED
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(icon, color="white", size=20),
                ft.Text(message, color="white", size=15, weight=ft.FontWeight.W_500),
            ], spacing=10),
            bgcolor=bg_color,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=20,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        self.page.snack_bar.open = True
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False; self.page.update()


def main(page: ft.Page):
    # Inicializar sistema antes de mostrar la interfaz
    if not initialize_system():
        # Mostrar error si no se pudo inicializar
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR, size=80, color="#EF4444"),
                    ft.Text("❌ Error de Conexión", size=32, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.Text(
                        "No se pudo conectar a la base de datos.\n"
                        "Verifica que SQL Server esté corriendo y la configuración en connection_data.json",
                        text_align=ft.TextAlign.CENTER,
                        color="#6B7280",
                        size=14
                    ),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        "Reintentar",
                        on_click=lambda e: page.window_close(),
                        bgcolor="#3B82F6",
                        color="#FFFFFF"
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        )
        return
    
    # Si todo está OK, iniciar la aplicación
    app = SistemaGestionApp(page)


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Iniciando Sistema de Gestión de Ventas SJG")
    print("=" * 60)
    ft.app(target=main)
