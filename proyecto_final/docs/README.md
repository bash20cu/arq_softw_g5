# Proyecto Final - Guia de trabajo

## Base de referencia

Este documento se construye a partir del enunciado ubicado en `proyecto_final/docs/Enunciado PROYECTO ASA.docx`.

Por el estado actual de `trabajo_en_clase`, la ruta mas conveniente para el equipo 5 es desarrollar el **Caso 1**, orientado a una empresa distribuidora con sitio web, administracion de productos, clientes, pedidos, control de inventario y consulta de estado de compras.

## Objetivo del proyecto

Construir un sistema web en arquitectura por capas con enfoque MVC que permita:

- presentar informacion de la empresa y sus productos;
- administrar inventario, clientes y pedidos;
- soportar registro de usuarios internos y registro autonomo de clientes;
- controlar estados de compra y consulta de pedidos;
- documentar formalmente el trabajo segun las exigencias del curso.

## Pautas a seguir

1. Mantener separacion estricta entre `trabajo_en_clase` y `proyecto_final`.
2. Reutilizar solo lo que aporte valor directo al Caso 1.
3. No copiar modulos completos sin antes validar si cumplen con el enunciado actual.
4. Priorizar evidencia academica ademas del software: cronograma, requerimientos, base de datos, casos de uso y bitacoras.
5. Alinear la implementacion tecnica con lo solicitado por el docente:
   - arquitectura en capas o MVC;
   - base de datos final en MSSQL Server Express;
   - documento formal en Word con APA 7;
   - prototipo funcional para el segundo avance;
   - presentacion final y defensa oral.
6. Tratar `trabajo_en_clase` como insumo de analisis, no como entrega final.

## Entregables del curso

### Entregable 1

- Cronograma con fechas y asignaciones.

### Entregable 2

- Introduccion.
- Levantamiento de requerimientos.
- Diseno de base de datos.
- Casos de uso.
- Bitacoras firmadas.

### Entregable 3

- Diseno de pantallas.
- Prototipo funcional al 80%.
- Bitacoras firmadas.

## Matriz de riesgo y reutilizacion desde `trabajo_en_clase`

| Componente actual | Que tenemos | Potencial de reutilizacion | Riesgo | Accion recomendada |
| --- | --- | --- | --- | --- |
| API de usuarios y autenticacion | Login, sesiones, registro, roles, pruebas | Alto | Medio | Reutilizar base de autenticacion y ajustar roles y permisos al caso final |
| Modulo de clientes | CRUD y endpoints | Alto | Bajo | Reutilizar casi completo, agregando categorias del enunciado |
| Modulo de productos | CRUD y stock | Alto | Medio | Reutilizar estructura, pero agregar fotografia, colores/estilos, IVA, codigo de barras y ubicacion en bodega |
| Modulo de ordenes | Registro de orden y detalle, descuento de stock | Alto | Medio | Reutilizar logica central y adaptar estados a `En preparacion`, `Listo para envio o recoleccion`, `Entregado` |
| Modelo de base de datos actual | Persona, usuario, cliente, producto, orden, detalle, factura, campania | Medio-Alto | Alto | Tomarlo como punto de partida, pero redisenar para MSSQL y cerrar brechas con requerimientos faltantes |
| Catalogos geograficos | Provincias, cantones, distritos | Medio | Bajo | Reutilizar si el caso final mantiene direccion estructurada |
| Frontend administrativo | Listados, formularios, panel principal | Medio | Medio | Reutilizar patrones y flujo, pero redisenar pantallas del sitio publico y branding segun paleta del enunciado |
| Campanias y soporte | Modulos adicionales no obligatorios para Caso 1 | Bajo | Medio | No priorizar en avance 1; solo rescatar ideas o estructuras utiles |
| Pruebas automatizadas | API, integracion y E2E basicas | Alto | Bajo | Reutilizar enfoque y adaptar pruebas al dominio final |
| Base de datos Docker/Postgres | Scripts y modelo actual | Medio | Alto | Util para desarrollo local, pero debe planearse migracion a MSSQL Server Express para la entrega |

## Brechas detectadas frente al enunciado

- El sistema actual no evidencia MSSQL Server Express como base oficial.
- Faltan atributos clave de producto: fotografia, colores o estilos, IVA, codigo de barras y ubicacion en bodega.
- Falta una pantalla publica completa con informacion corporativa, mision, vision, contacto y ubicacion.
- La clasificacion de clientes del enunciado no coincide con la estructura actual.
- Los estados de pedido actuales no coinciden exactamente con los del caso.
- No se observa una consulta publica o de cliente para revisar estado del pedido.
- No se evidencia integracion con camara o lector para codigo de barras.
- Hace falta formalizar logo, lineamiento visual y diseno alineado a la paleta del caso.
- La documentacion academica aun no esta consolidada dentro de `proyecto_final`.

## Cronograma propuesto

Tomando como referencia la fecha final del proyecto indicada en el enunciado, **14/04/2026**, se propone el siguiente plan:

| Fecha objetivo | Tarea | Responsable sugerido | Resultado esperado |
| --- | --- | --- | --- |
| 21/03/2026 | Revisar enunciado, elegir caso y ordenar repositorio | Equipo completo | Base del proyecto y alcance acordado |
| 22/03/2026 | Inventario de reutilizacion de `trabajo_en_clase` | Lider tecnico + apoyo backend | Lista de modulos reutilizables y brechas |
| 23/03/2026 | Definir requerimientos funcionales y no funcionales | Analisis/documentacion | Borrador de levantamiento de requerimientos |
| 24/03/2026 | Ajustar modelo conceptual y logico de datos | Backend + base de datos | Version inicial del modelo final |
| 25/03/2026 | Redactar casos de uso principales | Analisis/documentacion | Casos de uso de productos, clientes, pedidos y consulta |
| 26/03/2026 | Preparar cronograma y bitacora 1 | Lider + secretaria documental | Evidencia formal para avance 1 |
| 27/03/2026 | Migrar base tecnica minima a `proyecto_final` | Backend | Estructura inicial del proyecto final |
| 28/03/2026 | Adaptar autenticacion, roles y modulo de clientes | Backend | Base funcional del acceso y clientes |
| 29/03/2026 | Adaptar modulo de productos al enunciado | Backend + frontend | CRUD de productos con campos requeridos |
| 30/03/2026 | Adaptar modulo de pedidos e inventario | Backend | Flujo de compra con reduccion de stock |
| 31/03/2026 | Disenar pantallas publicas y administrativas | Frontend/UX | Propuesta visual del sitio |
| 01/04/2026 | Implementar pagina publica e identidad visual | Frontend | Inicio del sitio con informacion corporativa |
| 02/04/2026 | Implementar consulta de estado de pedidos | Backend + frontend | Pantalla funcional para seguimiento |
| 03/04/2026 | Definir estrategia de codigo de barras | Equipo tecnico | Decision tecnica documentada |
| 04/04/2026 | Preparar bitacoras 2 y 3 | Lider + equipo | Evidencia firmable actualizada |
| 05/04/2026 | Ejecutar pruebas tecnicas y corregir brechas | QA + backend | Sistema estable para demostracion |
| 06/04/2026 | Completar documento de avance | Documentacion | Entrega escrita casi cerrada |
| 07/04/2026 | Refinar prototipo al 80% | Equipo completo | Segundo avance funcional |
| 08/04/2026 | Preparar bitacoras 4 y 5 | Lider + equipo | Evidencia completa |
| 09/04/2026 | Revisar APA 7, portada y conclusiones | Documentacion | Documento formal listo |
| 10/04/2026 | Preparar PPT y guion de exposicion | Equipo completo | Material de presentacion listo |
| 11/04/2026 - 13/04/2026 | Ajustes finales, ensayo y validacion | Equipo completo | Entrega final depurada |
| 14/04/2026 | Entrega final | Equipo completo | Proyecto entregado |

## Tareas por frente

### Analisis y documentacion

- Elegir formalmente el Caso 1 como alcance del proyecto.
- Redactar introduccion, necesidad del negocio y herramientas usadas.
- Consolidar requerimientos funcionales y no funcionales.
- Elaborar casos de uso y anexar bitacoras.
- Preparar conclusiones y recomendaciones.

### Base de datos

- Convertir el modelo actual a una propuesta compatible con MSSQL Server Express.
- Incorporar campos faltantes para productos, pedidos e inventario.
- Revisar claves, restricciones y catalogos.
- Generar diagrama entidad-relacion final.

### Backend

- Reutilizar autenticacion, usuarios, clientes, productos y ordenes.
- Ajustar reglas de negocio al enunciado.
- Incorporar consulta de pedido para clientes.
- Revisar permisos por tipo de usuario interno y cliente.

### Frontend

- Crear pagina publica con empresa, ubicacion, contactos, mision y vision.
- Adaptar formularios y listados al caso final.
- Preparar interfaz de consulta de pedidos.
- Aplicar identidad visual con la paleta: negro, amarillo, blanco, dorado y naranja.

### Calidad

- Reusar pruebas existentes como base.
- Crear pruebas para pedidos, inventario y consulta de estado.
- Validar que el prototipo soporte una demo estable.

## Recomendacion inmediata

El siguiente paso mas rentable es crear en `proyecto_final` una primera copia controlada de solo estos bloques de `trabajo_en_clase`:

- autenticacion y usuarios;
- clientes;
- productos;
- ordenes;
- pruebas base;
- esquema de base de datos como borrador.

No conviene pasar todavia los modulos de campanias y soporte, porque aumentan complejidad y no son esenciales para el Caso 1.

## Decision de alcance asumida

Este plan asume que el equipo 5 desarrollara el **Caso 1** del enunciado, por ser el que mejor coincide con lo ya construido en `trabajo_en_clase`.
