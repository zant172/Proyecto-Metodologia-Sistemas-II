# 🏪 Sistema de Gestión de Ventas SJG

Sistema completo de punto de venta y gestión empresarial desarrollado con **Flet** (Python) y **SQL Server**.

## ✨ Características Principales

### 📊 Gestión Completa
- **Dashboard interactivo** con métricas en tiempo real
- **Control de inventario** con alertas de stock bajo
- **Punto de venta** con carrito de compras y múltiples métodos de pago
- **Gestión de caja** con apertura, pausa y cierre formal diario
- **Registro de gastos** con categorías y notas
- **Reportes financieros** con gráficos y análisis

### 👥 Gestión de Usuarios
- Sistema de roles: **Dev**, **Admin**, **Usuario**
- Autenticación segura con **bcrypt**
- Permisos granulares por rol
- Menú de usuario interactivo

### 🎨 Interfaz Moderna
- Diseño limpio y profesional
- Paleta de colores personalizada
- Pantalla de login con gradiente
- Tarjetas métricas con íconos
- Navegación intuitiva
- Responsive y optimizada

### 🔒 Seguridad
- Encriptación de contraseñas (bcrypt)
- Validación de SQL injection
- Transacciones de base de datos seguras
- Gestión de sesiones

## 🚀 Instalación

### Requisitos
- Python 3.8+
- SQL Server 2019+ (o SQL Server Express)
- ODBC Driver 18 for SQL Server

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/zant172/Proyecto-Metodologia-Sistemas-II.git
cd Proyecto-Metodologia-Sistemas-II
```

### Paso 2: Instalar dependencias
```bash
pip install flet pyodbc bcrypt
```

### Paso 3: Configurar SQL Server
Asegúrate de tener SQL Server instalado y en ejecución.

### Paso 4: Ejecutar la aplicación
```bash
python main.py
```

## 📖 Primer Uso

### Setup Automático
Al ejecutar por primera vez, el sistema:
1. **Detecta** si hay una conexión guardada
2. **Crea automáticamente** la base de datos `sistemgestionvntsjg`
3. **Genera todas las tablas** y relaciones necesarias
4. **Crea roles** predeterminados (Dev, Admin, Usuario)
5. **Inserta métodos de pago** iniciales
6. **Guía** para crear el primer usuario administrador

### Asistente de Configuración
Si no hay configuración previa, el asistente te guiará:
1. **Información del negocio** (nombre, tipo)
2. **Conexión a la base de datos** (servidor, autenticación)
3. **Creación del super admin** (primer usuario)

## 🗂️ Estructura del Proyecto

```
Proyecto-Metodologia-Sistemas-II/
├── main.py                          # Aplicación principal (Flet)
├── connection_data.json             # Configuración de conexión (auto-generado)
├── app/
│   ├── auth.py                      # Autenticación y usuarios
│   ├── caja_logic.py                # Lógica de caja
│   ├── dashboard_logic.py           # Métricas y cierres formales
│   ├── database.py                  # Conexión y esquema
│   ├── gastos.py                    # Gestión de gastos
│   ├── metodos_pago.py              # Métodos de pago
│   ├── products.py                  # Gestión de productos
│   ├── reportes.py                  # Reportes financieros
│   └── sales_logic.py               # Procesamiento de ventas
├── migrate_add_nota_gastos.py       # Script de migración (columna Nota)
└── README.md                        # Este archivo
```

## 💾 Base de Datos

### Tablas Principales
- **Usuarios** - Gestión de usuarios y roles
- **Productos** - Inventario con categorías
- **Cajas** - Control de cajas operativas
- **Ventas / DetalleVentas** - Transacciones de venta
- **Gastos** - Registro de gastos con notas
- **CierresDeCaja** - Cierres formales diarios
- **MetodosPago** - Formas de pago configurables

### Diagrama de Relaciones
```
Usuarios ←→ Ventas ←→ DetalleVentas ←→ Productos
    ↓         ↓
  Cajas   MetodosPago
    ↓
CierresDeCaja ←→ CierresDeCajaDetalle
```

## 🎯 Funcionalidades por Módulo

### Dashboard
- 📈 Métricas del día actual
- 📊 Gráfico de ventas por producto
- 💰 Resumen de ventas, gastos y balance
- 🔄 Actualización en tiempo real

### Productos
- ➕ CRUD completo de productos
- 🏷️ Gestión de categorías
- 🔍 Búsqueda y filtrado
- ⚠️ Alertas de stock bajo
- 📦 Control de inventario

### Ventas (POS)
- 🛒 Carrito de compras interactivo
- 🔢 Selección de cantidades con validación de stock
- 💳 Múltiples métodos de pago
- 🧾 Generación automática de ventas
- ✅ Validación de caja abierta

### Caja
- 🔓 Apertura de caja por turno
- ⏸️ Pausa/Reanudación
- 🔒 Cierre formal con registro permanente
- 📋 Historial de cajas y cierres
- 💵 Desglose por método de pago

### Gastos
- ➕ Registro de gastos con categorías
- 📝 Campo de notas opcional
- 🗂️ 7 categorías predefinidas
- 🗑️ Eliminación con confirmación
- 📅 Vista de últimos 30 gastos

### Reportes
- 📊 Rango de fechas personalizado
- 💰 Resumen financiero detallado
- 🏆 Top 5 productos más vendidos
- 💳 Desglose por método de pago
- 📈 Visualización con tablas

### Usuarios (Admin)
- 👥 Gestión completa de usuarios
- 🔐 Asignación de roles
- ✏️ Edición de perfiles
- 🗑️ Eliminación de usuarios

## 🛡️ Roles y Permisos

### Dev (Desarrollador)
- ✅ Acceso total al sistema
- ✅ Todas las funcionalidades habilitadas

### Admin (Administrador)
- ✅ Gestión de usuarios
- ✅ Acceso a reportes
- ✅ Control de gastos y métodos de pago
- ✅ Todas las operaciones de venta

### Usuario (Empleado)
- ✅ Dashboard operativo
- ✅ Gestión de productos
- ✅ Punto de venta
- ✅ Gestión de caja
- ❌ Sin acceso a reportes ni gestión de usuarios

## 🔧 Migración de Bases de Datos Existentes

Si tienes una base de datos creada antes de las últimas actualizaciones:

```bash
python migrate_add_nota_gastos.py
```

Este script agrega la columna `Nota` a la tabla `Gastos`.

## 📝 Notas Técnicas

### Paleta de Colores
```python
Primary:   #6366F1  (Índigo)
Success:   #10B981  (Verde)
Warning:   #F59E0B  (Ámbar)
Danger:    #EF4444  (Rojo)
Info:      #3B82F6  (Azul)
```

### Configuración de Ventana
- Tamaño inicial: 1600x1000
- Tamaño mínimo: 1200x700
- Modo: Claro (light mode)

## 🤝 Contribuciones

Este proyecto es parte de un trabajo académico para Metodología de Sistemas II.

## 📄 Licencia

Proyecto académico - SJG Solutions © 2025

## 👨‍💻 Autor

**zant172** - [GitHub](https://github.com/zant172)

---

**v1.0** - Sistema de Gestión de Ventas SJG
