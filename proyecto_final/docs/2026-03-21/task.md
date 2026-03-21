# Task Plan - 2026-03-21

## Contexto

El equipo 5 trabajara el **Caso 5: ProPat S.A.**

Objetivo inmediato:

- levantar un backend funcional;
- conectarlo a MSSQL en la VM Debian ya disponible;
- dejar una base de datos utilizable;
- construir un frontend rustico suficiente para demo;
- preparar la base tecnica para luego integrar pasarela de pagos.

## Alcance tecnico de esta fase

Debemos dejar operativo lo siguiente:

- autenticacion de empleados y clientes;
- registro autonomo de clientes;
- catalogo de productos;
- gestion de pedidos;
- rebajo automatico de inventario;
- consulta de estado de pedidos;
- estructura inicial para pasarela de pagos;
- frontend simple para operar el flujo.

## Prioridad de ejecucion

1. Base de datos MSSQL para Caso 5.
2. Conexion del backend a MSSQL.
3. Estructura minima del proyecto en `proyecto_final`.
4. Modulo de autenticacion y roles.
5. Modulo de productos.
6. Modulo de clientes.
7. Modulo de pedidos e inventario.
8. Modulo base de pagos.
9. Consulta de estado de pedidos.
10. Frontend rustico para demo.

## Tareas inmediatas

### 1. Preparar base tecnica en `proyecto_final`

- Crear estructura inicial del backend.
- Copiar solo los modulos reutilizables desde `trabajo_en_clase`.
- Excluir por ahora campanias y soporte.
- Definir archivo de configuracion para entorno local y VM.

Resultado esperado:

- backend base ejecutando desde `proyecto_final`.

### 2. Conectar a MSSQL Server

- Confirmar host, puerto, nombre de base, usuario y password de la VM Debian.
- Definir driver a usar desde Python.
- Preparar cadena de conexion para MSSQL.
- Probar conexion desde la aplicacion.

Resultado esperado:

- aplicacion conectando exitosamente a MSSQL.

## Datos que debemos tener listos de la VM

- IP o hostname de la VM.
- Puerto expuesto de MSSQL.
- Nombre de la base de datos.
- Usuario de SQL Server.
- Password.
- Driver disponible en la maquina local o entorno de ejecucion.

### 3. Adaptar modelo de base de datos al Caso 5

Tablas minimas:

- `usuarios`
- `roles`
- `clientes`
- `productos`
- `pedidos`
- `detalle_pedido`
- `pagos`

Campos clave que no debemos olvidar:

- producto: nombre, descripcion, fotografia, color_estilo, stock, precio_base, iva, precio_final, codigo_barras.
- cliente: nombre, direccion, telefono, correo.
- pedido: cliente, fecha, estado, total.
- pago: pedido, proveedor, referencia, monto, estado, fecha.

Estados de pedido requeridos:

- `En preparacion`
- `Listo para envio o recoleccion`
- `Entregado al cliente`

Resultado esperado:

- script inicial de base de datos alineado al Caso 5.

### 4. Reutilizar y adaptar autenticacion

- Reusar login y sesiones del trabajo en clase.
- Ajustar roles minimos:
  - empleado
  - cliente
- Mantener acceso administrativo solo para empleados.

Resultado esperado:

- login funcional y rutas protegidas.

### 5. Reutilizar y adaptar productos

- Reusar CRUD existente como base.
- Agregar campos faltantes del Caso 5.
- Asegurar que el stock sea consistente.
- Preparar salida JSON y vista simple HTML.

Resultado esperado:

- productos listables, creables y editables.

### 6. Reutilizar y adaptar clientes

- Mantener registro interno.
- Agregar registro autonomo para cliente.
- Validar datos minimos requeridos.

Resultado esperado:

- clientes creados desde admin y desde registro publico.

### 7. Reutilizar y adaptar pedidos

- Registrar compra.
- Guardar detalle de productos.
- Calcular total.
- Rebajar inventario automaticamente.
- Asignar estado inicial.

Resultado esperado:

- flujo de pedido funcional de punta a punta.

### 8. Preparar integracion inicial de pagos

- Definir una tabla o modelo de pagos.
- Dejar interfaz de servicio para pasarela.
- Permitir registrar pago en estado de prueba.
- Elegir sandbox o trial despues.

Resultado esperado:

- arquitectura lista para integrar la pasarela sin rehacer pedidos.

### 9. Consulta de estado de pedido

- Crear endpoint para consultar pedido por identificador.
- Mostrar estado, fecha y resumen de productos.
- Habilitar acceso al cliente autenticado.

Resultado esperado:

- pantalla o endpoint funcional para seguimiento de compras.

### 10. Frontend rustico

Pantallas minimas:

- inicio publico;
- catalogo de productos;
- login;
- registro de cliente;
- listado de pedidos;
- consulta de estado;
- panel admin basico;
- formulario de producto;
- formulario de pedido.

Criterio:

- HTML simple;
- estilos minimos;
- enfoque en funcionalidad y demo.

Resultado esperado:

- demo navegable aunque sin acabado final.

## Orden sugerido de ejecucion por dias

### Dia 1

- estructura de `proyecto_final`
- configuracion de entorno
- conexion a MSSQL
- script base de BD

### Dia 2

- autenticacion
- roles
- usuarios
- clientes

### Dia 3

- productos
- inventario
- frontend rustico de catalogo y admin

### Dia 4

- pedidos
- detalle de pedido
- rebajo automatico de stock

### Dia 5

- modelo de pagos
- simulacion de flujo de pago
- consulta de estado de pedido

### Dia 6

- pruebas tecnicas
- correccion de errores
- ajuste del frontend rustico

## Riesgos inmediatos

| Riesgo | Impacto | Mitigacion |
| --- | --- | --- |
| La conexion a MSSQL falla por driver o red | Alto | Probar conexion aislada primero antes de mover mucho codigo |
| El esquema actual de clase depende de Postgres | Alto | Adaptar SQL temprano y evitar acoplar nueva logica a sintaxis especifica de Postgres |
| La pasarela de pagos consume mas tiempo del esperado | Alto | Dejar interfaz y modelo listos desde el inicio; integrar sandbox despues |
| El frontend se lleva demasiado tiempo | Medio | Mantenerlo rustico y priorizar formularios funcionales |
| Copiar demasiado codigo desde `trabajo_en_clase` genera ruido | Medio | Migrar solo autenticacion, clientes, productos, pedidos y pruebas base |

## Checklist de inicio

- [ ] Confirmar credenciales y acceso a la VM Debian con MSSQL.
- [ ] Confirmar driver Python para MSSQL.
- [ ] Crear estructura tecnica base en `proyecto_final`.
- [ ] Definir modelo de datos del Caso 5.
- [ ] Migrar autenticacion.
- [ ] Migrar clientes.
- [ ] Migrar productos.
- [ ] Migrar pedidos.
- [ ] Crear modelo base de pagos.
- [ ] Habilitar frontend rustico.

## Nota de trabajo

La prioridad no es el acabado visual. La prioridad es demostrar que el Caso 5 funciona con base de datos, autenticacion, flujo de compra, inventario y base para pagos.
