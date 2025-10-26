ACTA DE CONSTITUCIÓN DEL PROYECTO



Carrera: Tecnicatura Universitaria en Programación
Materia: Metodología de Sistemas II – UTN FRT – Año 2025
Proyecto: Sistema de Gestión de Ventas – InfinityTech
Fecha: 14/10/2025
Equipo de trabajo:
Product Owner: Jael Bazán


Scrum Master: Santiago Rojas


Developer: Gabriela Cabello


Justificación / Propósito
El proyecto InfinityTech surge de la necesidad de modernizar y optimizar la gestión de un negocio de artículos tecnológicos. Actualmente, el control de ventas, stock y reportes financieros se realiza de manera manual o con herramientas dispersas, lo cual genera errores, demoras e inconsistencias en la información.
Con este sistema se busca digitalizar el proceso, centralizando toda la información en una única plataforma que permita al dueño del negocio mantener un inventario ordenado, conocer su rentabilidad mensual y mejorar la toma de decisiones a través de reportes precisos.
Objetivo General
Desarrollar un sistema informático que gestione de forma integral las ventas, el stock y los reportes financieros del comercio InfinityTech, permitiendo automatizar procesos, reducir errores y mejorar el control operativo y económico del negocio.
 Objetivos Específicos
Implementar un módulo de registro, modificación y eliminación de productos.


Permitir la administración de ventas en tiempo real con actualización automática del stock.


Incorporar un sistema de generación de reportes mensuales de ingresos y egresos.


Ofrecer alertas automáticas de productos con stock bajo.


Desarrollar una interfaz intuitiva que facilite el uso para usuarios administrativos y vendedores.








Alcance y Limitaciones
Alcance:
Gestión de productos, categorías y proveedores.


Control de stock y actualizaciones automáticas tras cada venta.


Registro y administración de ventas.


Generación de reportes económicos mensuales.


Control de usuarios con diferentes niveles de permiso.


Limitaciones:
No incluirá gestión contable avanzada ni facturación electrónica en esta versión.


No contempla integración con sistemas de envío o logística externos.


 Entregables Principales
Documento de Requerimientos Funcionales y No Funcionales.


Diagramas de Base de Datos y Modelado UML.


Interfaz de usuario (prototipos o mockups).


Código fuente en repositorio GitHub.


Manual de Usuario y Manual Técnico.


Informe de pruebas funcionales.


Presentación final del proyecto ante el docente.





Roles y Responsabilidades
 
Rol
Integrante
Responsabilidades
Product Owner
Jael Bazán
Define las prioridades, valida entregables y mantiene el backlog actualizado.
Scrum Master
Santiago Rojas
Supervisa el cumplimiento de la metodología Scrum, coordina las reuniones y elimina impedimentos.
Developer
Gabriela Cabello
Diseña, programa, prueba y documenta los módulos del sistema.

 

Plan de Proyecto - 5 Sprints (21 de Octubre - 18 de Noviembre)

Sprint 1: Planeación, Diseño y Estructura (21 - 25 de Octubre)
• Objetivo del Sprint: Formalizar el alcance, las herramientas de gestión y establecer los "planos" conceptuales y físicos del sistema (diseño de la base de datos).
• Entregables:
• Acta de Constitución del Proyecto (Project Charter): Define problema, objetivos, alcance, stakeholders y funcionalidades principales.
• Configuración del Repositorio: Repositorio en GitHub creado y poblado con la estructura de carpetas inicial.
• Tablero de Trello: Creado y poblado con las tarjetas iniciales de las épicas y los 5 sprints.
• Definición de la Pila Tecnológica: Documento que oficializa el uso de Python, PyQt6, SQL Server, etc.
• Diagrama Entidad-Relación (ERD): Diseño visual final de la base de datos, con tablas, columnas y sus relaciones.
• Diccionario de Datos: Documento que describe cada tabla, columna y tipo de dato de la base de datos.
Sprint 2: Interfaz, Casos de Uso y Fundación de la DB (28 de Octubre - 1 de Noviembre)
• Objetivo del Sprint: Definir el diseño visual de la aplicación, detallar las interacciones del usuario y establecer la base de datos funcional en el servidor.
• Entregables:
• Wireframes o Mockups de la Interfaz (UI): Bocetos o diseños de baja/media fidelidad de las pantallas clave (Login, Ventana Principal, Stock, Ventas).
• Casos de Uso: Descripción detallada de las interacciones clave del usuario con el sistema (ej. "Caso de Uso: Realizar una Venta", "Caso de Uso: Gestionar un Producto").
• Base de Datos Funcional: El script SQL de creación de tablas ejecutado y verificado en SQL Server, listo para ser poblado.
Sprint 3: Fundación Técnica y Autenticación (4 - 8 de Noviembre)
• Objetivo del Sprint: Construir la capa de conectividad y seguridad del sistema para entregar la primera funcionalidad tangible: un sistema de login seguro y funcional.
• Entregables:
• Módulos de Backend (database.py, auth.py): Código funcional para la conexión a SQL Server y la autenticación segura (hashing y verificación de contraseñas).
• Ventana de Login Funcional: Interfaz gráfica que valida las credenciales del usuario contra la base de datos.
• Ventana Principal Básica: Una ventana de bienvenida que se abre tras un login exitoso y muestra el rol del usuario autenticado.
Sprint 4: Gestión de Inventario (CRUD de Productos) (11 - 15 de Noviembre)
• Objetivo del Sprint: Implementar la funcionalidad completa para que los administradores puedan gestionar el catálogo de productos (CRUD).
• Entregables:
• Módulo de "Stock" funcional: Una sección en la app que muestra la lista de productos en una tabla.
• Formularios de Creación, Edición y Eliminación: Ventanas emergentes para agregar nuevos productos, modificar los existentes y darlos de baja (soft delete o eliminación).
• Control de Acceso Implementado: Verificación del rol del usuario. Los botones para "Agregar" y "Editar" productos están deshabilitados u ocultos para usuarios con rol limitado ("Usuario" simple).
Sprint 5: Módulo de Venta (POS), Usuarios y Reportes (18 de Noviembre)
• Objetivo del Sprint: Desarrollar el corazón operativo (punto de venta), las funcionalidades administrativas restantes (gestión de personal) y la capa de análisis básico.
• Entregables:
• Módulo de "Ventas" funcional: Interfaz con buscador de productos, gestión de cantidades y carrito de compras.
• Lógica de Transacción: Al finalizar una venta, el stock en la base de datos se actualiza correctamente.
• Registro de Ventas: Cada venta se guarda correctamente en las tablas Ventas y DetalleVentas.
• Gestión de Usuarios (CRUD): Implementación de un módulo (solo visible para "Admin") que permite crear, editar y asignar roles a otros usuarios.
• Reportes/Consultas Básicas: Al menos una vista de reporte simple (ej. Top 10 productos más vendidos o Ventas por rango de fecha).
●Entregables:
Carpeta Final del Proyecto: Un archivo ZIP o una carpeta que contiene:
■ Documentación Final:
 Manual de Usuario: Guía para el cliente final sobre cómo usar el programa.
 Manual Técnico: Explicación de la arquitectura, base de datos y código para otros desarrolladores. 
Código Fuente Completo: Todo el proyecto de Python.
Instalador del Programa: El archivo .exe final.    
Presentación Final: Diapositivas (PowerPoint, Google Slides) para la defensa del proyecto.
Proyecto Validado: El software es presentado, cumple con todos los objetivos definidos en el Sprint 1 y es aprobado.

Criterios de Éxito
El sistema debe permitir registrar una venta en menos de 2 minutos.


Los reportes mensuales deben generarse automáticamente y mostrar ingresos, egresos y balance.


El sistema debe tener un tiempo de disponibilidad del 95% durante las pruebas.


Debe mantener la integridad de datos en todas las operaciones de stock y ventas.


La interfaz debe ser clara y navegable, validada por usuarios de prueba.




Riesgos Iniciales
Retrasos en la integración de módulos debido a tiempo académico limitado.


Posibles errores de sincronización entre stock y ventas.


Falta de experiencia previa en reportes automatizados.


Riesgo de pérdida de datos si no se realizan copias de seguridad periódicas.



 Aprobación
Docente Coordinador: Esper Rodrigo
Firma / Validación: ___________________________
Fecha: ___________________________


