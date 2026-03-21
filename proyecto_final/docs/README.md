# Proyecto Final - Base para documento escrito

## Proposito de este documento

Este README funciona como base de contenido para la parte escrita del proyecto final. La idea es que el equipo pueda tomar esta estructura, adaptarla al formato Word solicitado por el docente y completar portada, APA 7, bibliografia, bitacoras y anexos.

## Referencia academica

Segun el enunciado del curso, el documento formal debe contener como minimo:

- portada;
- detalle de la necesidad;
- descripcion de las herramientas utilizadas para el desarrollo del sistema;
- detalle de la arquitectura planteada;
- detalle de los componentes del sistema;
- al menos 3 conclusiones;
- al menos 3 recomendaciones.

Ademas, los entregables del proyecto incluyen:

- cronograma con fechas y asignaciones;
- introduccion;
- levantamiento de requerimientos;
- diseño de base de datos;
- casos de uso;
- diseño de pantallas;
- prototipo funcional al 80%;
- bitacoras firmadas.

## Caso seleccionado

El equipo 5 desarrolla el **Caso 5: ProPat S.A.**

### Resumen del caso

La empresa ProPat S.A. requiere un sistema web de ventas que incluya:

- presentacion de informacion de la empresa;
- contactos;
- mision y vision;
- catalogo de productos;
- registro de clientes;
- gestion de pedidos;
- reduccion automatica del inventario;
- estados de compra;
- integracion con una pasarela de pagos de prueba;
- consulta del estado del pedido;
- acceso diferenciado entre clientes y empleados.

## Introduccion

El presente proyecto corresponde al curso Arquitectura del Software y tiene como objetivo desarrollar una solucion web para la empresa ficticia ProPat S.A. El sistema busca apoyar el proceso de ventas en linea mediante la gestion de productos, clientes, pedidos y pagos electronicos en un entorno estructurado bajo arquitectura por capas con enfoque MVC.

Como parte del trabajo realizado por el equipo 5, se tomo como punto de partida el material previo desarrollado en `trabajo_en_clase`, separando claramente el nuevo desarrollo dentro de `proyecto_final` para evitar mezclar entregables. A partir de esa base se adapto la solucion para alinearla con los requerimientos del Caso 5, migrando el enfoque tecnico hacia MSSQL Server y añadiendo integracion inicial con PayPal Sandbox.

## Detalle de la necesidad

ProPat S.A. necesita una plataforma que le permita vender productos por medio de la web y administrar de manera organizada los procesos asociados a una compra digital. La empresa requiere mostrar su catalogo, registrar clientes, recibir pedidos, controlar el inventario y permitir el seguimiento de estados de compra.

Adicionalmente, el caso exige integrar una pasarela de pagos con modalidad de prueba o sandbox, de forma que el sistema pueda crear y procesar intentos de pago electronico sin depender de cobros reales. Esto hace necesario un diseño que contemple seguridad, persistencia de datos, control de roles y una interfaz inicial tanto para clientes como para personal interno.

## Objetivo general

Desarrollar un sistema web de ventas para ProPat S.A. utilizando arquitectura por capas y base de datos MSSQL Server, permitiendo la administracion de productos, clientes, pedidos y pagos en linea.

## Objetivos especificos

- Implementar una base de datos relacional en MSSQL Server para soportar el dominio del sistema.
- Permitir registro autonomo de clientes y autenticacion de usuarios.
- Gestionar productos con informacion comercial e inventario.
- Registrar pedidos y reducir automaticamente el stock.
- Consultar el estado de pedidos desde el sistema.
- Integrar una pasarela de pago en modo sandbox para pruebas.
- Construir un frontend rustico inicial que consuma los servicios del backend.

## Herramientas utilizadas

### Backend

- Python 3.10.20
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- pyodbc
- python-dotenv

### Base de datos

- MSSQL Server
- ODBC Driver 18 for SQL Server

### Integracion de pagos

- PayPal Sandbox

### Pruebas y validacion

- Pytest
- Postman

### Frontend inicial

- HTML
- Bootstrap 5
- jQuery

### Entorno de trabajo

- VM con Debian y SQL Server configurado
- Desarrollo local en macOS para integracion y pruebas

## Arquitectura planteada

La solucion se organizo siguiendo una arquitectura por capas con enfoque MVC ligero:

### Capa de presentacion

Corresponde a las vistas HTML y a los endpoints HTTP expuestos por Flask. Incluye:

- pantallas publicas y administrativas en `app/views/templates`;
- rutas de frontend en `app/routes/frontend.py`;
- API REST en `app/routes/api_v1.py`.

### Capa de logica de negocio

Implementada mediante controladores que encapsulan reglas y validaciones:

- `auth_controller.py`
- `client_controller.py`
- `product_controller.py`
- `order_controller.py`
- `payment_controller.py`
- `user_controller.py`

### Capa de acceso a datos

Representada por los modelos SQLAlchemy y la gestion de sesion de base de datos:

- `app/models/user.py`
- `app/models/product.py`
- `app/models/order.py`
- `app/models/catalog.py`
- `app/database.py`

### Capa de persistencia e inicializacion

Incluye la configuracion de conexion e inyeccion automatica del esquema SQL:

- `app/config.py`
- `app/db_bootstrap.py`
- `app/sql/schema.sql`
- `app/sql/seed.sql`

## Componentes del sistema

### 1. Modulo de autenticacion

Permite:

- verificar credenciales;
- crear sesion para usuarios autenticados;
- registrar clientes desde interfaz publica;
- cerrar sesion.

### 2. Modulo de usuarios y roles

Gestiona:

- usuarios administrativos;
- empleados;
- clientes;
- control de acceso por rol.

### 3. Modulo de clientes

Permite:

- registrar clientes;
- mantener informacion de contacto;
- consultar clientes existentes;
- asociar registros de cliente con datos de persona.

### 4. Modulo de productos

Permite:

- crear productos;
- listar productos;
- mantener stock;
- registrar descripcion, codigo de barras, fotografia, color o estilo, precio base e IVA.

### 5. Modulo de ordenes

Permite:

- crear pedidos;
- asociar cliente y productos;
- calcular total;
- controlar estados de compra;
- reducir inventario automaticamente.

Estados implementados:

- `En preparacion`
- `Listo para envio o recoleccion`
- `Entregado al cliente`
- `Cancelado`

### 6. Modulo de pagos

Permite:

- registrar pagos asociados a una orden;
- crear ordenes de pago en PayPal Sandbox;
- almacenar referencia externa del proveedor;
- capturar pagos luego de aprobacion.

### 7. Modulo de consulta de pedidos

Permite consultar:

- identificador de pedido;
- estado;
- fecha;
- total.

### 8. Frontend rustico inicial

Se construyeron pantallas sencillas para:

- inicio;
- login;
- registro;
- panel principal;
- catalogo de productos;
- ordenes;
- consulta de pedido.

## Modelado de base de datos

El modelo inicial del Caso 5 se construyo en MSSQL Server considerando las siguientes entidades principales:

- `rol`
- `provincia`
- `canton`
- `distrito`
- `persona`
- `usuario`
- `cliente`
- `producto`
- `orden_compra`
- `detalle_orden`
- `pago`

### Relacion general

- una persona puede asociarse a un usuario;
- una persona puede asociarse a un cliente;
- un usuario pertenece a un rol;
- un pedido pertenece a un cliente y a un usuario;
- un pedido tiene muchos detalles;
- un detalle referencia un producto;
- un pago pertenece a una orden.

### Archivo base del esquema

El esquema actual se encuentra en:

- `proyecto_final/app/sql/schema.sql`

El seed inicial se encuentra en:

- `proyecto_final/app/sql/seed.sql`

## Requerimientos implementados al cierre de la jornada

Durante la jornada de trabajo del 21/03/2026 se avanzaron los siguientes puntos:

- separacion formal entre `trabajo_en_clase` y `proyecto_final`;
- configuracion del backend en `proyecto_final`;
- adaptacion de variables de entorno para MSSQL;
- conexion funcional a SQL Server;
- creacion automatica de la base de datos `SistemaVentas`;
- inyeccion del esquema SQL desde la aplicacion;
- seed inicial de roles y usuario administrador;
- API de salud, autenticacion, productos, clientes, usuarios y ordenes;
- consulta de estado de pedidos;
- integracion inicial con PayPal Sandbox;
- frontend rustico con Bootstrap y jQuery;
- documentacion de pruebas con Postman;
- pruebas automatizadas del backend.

## Pruebas realizadas

### Pruebas manuales

Se prepararon pruebas manuales con Postman en:

- `proyecto_final/docs/postman/README.md`

Estas pruebas cubren:

- login;
- registro de cliente;
- creacion de producto;
- creacion de orden;
- consulta de estado;
- flujo inicial de pagos.

### Pruebas automatizadas

Se implementaron pruebas en:

- `proyecto_final/tests/conftest.py`
- `proyecto_final/tests/test_backend_flow.py`

Resultados obtenidos:

- flujo completo del backend validado;
- validaciones de permisos comprobadas;
- errores de autenticacion comprobados;
- validacion de stock insuficiente comprobada;
- simulacion de pagos integrada en pruebas.

## Estado actual del prototipo

El sistema se encuentra en una fase funcional inicial. El backend ya permite demostrar la mayor parte del flujo principal del Caso 5 y el frontend rustico ofrece una base navegable para presentacion y pruebas.

### Lo que ya funciona

- arranque del sistema;
- conexion a MSSQL;
- creacion del esquema;
- autenticacion;
- CRUD basico de productos;
- registro de clientes;
- creacion y gestion de ordenes;
- consulta del estado de pedidos;
- generacion de ordenes PayPal Sandbox;
- frontend inicial para operar estos modulos.

### Lo que aun debe reforzarse

- mayor refinamiento visual;
- flujo completo de aprobacion y captura PayPal desde interfaz de usuario;
- mejoras en manejo de errores en frontend;
- ampliacion de pruebas;
- elaboracion formal de casos de uso y anexos academicos.

## Relacion con el enunciado

El avance desarrollado responde directamente a los requerimientos del Caso 5:

- sitio web: implementado en version rustica inicial;
- informacion de empresa, mision y vision: presentes en frontend inicial;
- registro de clientes: implementado;
- productos con atributos de venta: implementado en backend;
- pedidos y reduccion de inventario: implementado;
- estados de compra: implementado;
- consulta de estado de pedidos: implementado;
- pasarela de pagos de prueba: implementacion inicial con PayPal Sandbox.

## Conclusiones

1. La separacion entre `trabajo_en_clase` y `proyecto_final` permitio reorganizar el desarrollo sin perder el trabajo previo y facilitando una adaptacion mas ordenada al Caso 5.
2. La migracion hacia MSSQL Server y la inyeccion de un esquema SQL controlado fortalecieron la consistencia tecnica del proyecto y lo alinearon mejor con lo exigido por el curso.
3. La integracion inicial con PayPal Sandbox demuestra que el sistema ya no se limita a gestionar catalogo y pedidos, sino que incorpora una base realista para el proceso de pagos electronicos.

## Recomendaciones

1. Continuar con la evolucion del frontend para mejorar usabilidad, validaciones visuales y claridad del flujo de compra.
2. Documentar formalmente los casos de uso, diagrama de base de datos y arquitectura en formato Word con normas APA 7 para cumplir integralmente con el entregable academico.
3. Mantener y ampliar la suite de pruebas automaticas para proteger el sistema ante regresiones durante las siguientes fases del proyecto.

## Estructura sugerida para el Word

Se recomienda pasar este contenido a Word bajo esta estructura:

1. Portada
2. Introduccion
3. Detalle de la necesidad
4. Objetivo general y objetivos especificos
5. Herramientas utilizadas
6. Arquitectura planteada
7. Componentes del sistema
8. Diseño de base de datos
9. Avance implementado
10. Pruebas realizadas
11. Conclusiones
12. Recomendaciones
13. Bibliografia
14. Apendices y bitacoras

## Nota final

Este README no reemplaza el documento formal del curso, pero si concentra el contenido tecnico principal desarrollado hasta la fecha y puede usarse como base directa para la redaccion del entregable en Word.
