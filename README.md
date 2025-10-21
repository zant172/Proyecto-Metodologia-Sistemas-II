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

 


Cronograma Inicial (en Sprints)
Duración total estimada: 16 semanas
Metodología: Scrum (sprints de 2 a 3 semanas)

Sprint 1 (Semanas 1-2): Inicio del Proyecto y Definición del Tema
●Objetivo del Sprint: Formalizar el alcance, los objetivos y la planificación inicial del proyecto. Establecer las herramientas de gestión y el entorno   de trabajo.
●Entregables:
○Acta de Constitución del Proyecto (Project Charter): Un documento formal que define el problema, los objetivos, el alcance, los stakeholders (profesor, equipo) y las principales funcionalidades.
○Configuración del Repositorio: Repositorio en GitHub creado, con la estructura de carpetas inicial.
○Tablero de Trello: Creado y poblado con las tarjetas iniciales de las épicas y sprints.
○Definición de la Pila Tecnológica: Documento que oficializa el uso de Python, PyQt6, SQL Server, etc.
 Sprint 2 (Semanas 3-4): Análisis y Diseño del Sistema
●Objetivo del Sprint: Crear los "planos" del sistema antes de comenzar la construcción. Definir la arquitectura de la base de datos y el diseño visual de la aplicación.
●Entregables:
○Diagrama Entidad-Relación (ERD): El diseño visual final de la base de datos, mostrando todas las tablas, columnas y sus relaciones.
○Diccionario de Datos: Un documento que describe cada tabla y columna de la base de datos.
○Wireframes o Mockups de la Interfaz (UI): Bocetos o diseños de baja/media fidelidad de las pantallas principales (Login, Ventana Principal, Stock, Ventas).
○Casos de Uso: Descripción detallada de las interacciones clave del usuario con el sistema (ej."Caso de Uso: Realizar una Venta").
 Sprint 3 (Semanas 5-6): Fundación Técnica y Autenticación
●Objetivo del Sprint: Construir la base técnica del proyecto y entregar la primera funcionalidad tangible: un sistema de login seguro.
●Entregables:
Base de Datos Funcional: El script SQL ejecutado en SQL Server.
Módulos de Backend (database.py, auth.py): Código funcional para la conexión y la autenticación segura (hashing y verificación).
Ventana de Login Funcional: Interfaz gráfica que valida las credenciales del usuario contra la base de datos.
Ventana Principal Básica: Una ventana que se abre tras un login exitoso y muestra el rol del usuario.
 Sprint 4 (Semanas 7-8): Gestión de Inventario (CRUD de Productos)
●Objetivo del Sprint: Implementar la funcionalidad completa para que los administradores puedan gestionar el catálogo de productos.
●Entregables:
Módulo de "Stock" funcional: Una sección en la app que muestra los productos en una tabla.
Formularios de Creación y Edición: Ventanas emergentes para agregar nuevos productos o modificar los existentes.
Control de Acceso Implementado: Los usuarios con rol "Usuario" pueden ver el stock, pero los botones para "Agregar" y "Editar" están deshabilitados u ocultos.
Sprint 5 (Semanas 9-10): Módulo de Punto de Venta (POS)
●Objetivo del Sprint: Desarrollar la funcionalidad de ventas, el corazón operativo del sistema.
●Entregables:
Módulo de "Ventas" funcional: Una interfaz con un buscador de productos y un carrito de compras.
Lógica de Transacción: Al finalizar una venta, el stock en la base de datos se actualiza correctamente.
Registro de Ventas: Cada venta se guarda correctamente en las tablas Ventas y DetalleVentas.
 Sprint 6 (Semanas 11-12): Gestión de Usuarios y Reportes
● Objetivo del Sprint: Añadir las funcionalidades administrativas clave para la gestión de personal y el análisis de negocio.


●Entregables:
Módulo de "Gestión de Usuarios" funcional: Interfaz (visible solo para Admins) para crear nuevas cuentas de empleados (con rol "Usuario").
Módulo de "Reportes" básico: Una sección (visible solo para Admins) que muestra un reporte de ventas por fecha.
Sprint 7 (Semanas 13-14): Pruebas, Empaquetado y Refinamiento
●Objetivo del Sprint: Asegurar la calidad del software, corregir errores y crear una versión distribuible del programa.
●Entregables:
Informe de Pruebas: Un documento con los casos de prueba ejecutados y los bugs encontrados y solucionados.
Aplicación Compilada (.exe): Un archivo ejecutable creado con PyInstaller, listo para ser instalado en otra computadora.
Refinamiento de la Interfaz (UI/UX): Mejoras visuales y de usabilidad basadas en la retroalimentación.
Sprint 8 (Semanas 15-16): Documentación Final y Validación
●Objetivo del Sprint: Completar toda la documentación requerida, preparar la presentación final y obtener la validación del proyecto.
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


