# Cambios del 2026-04-01

## Resumen

Durante esta sesion se corrigieron problemas de seguridad, compatibilidad con SQL Server y el flujo funcional de pagos PayPal Sandbox para `proyecto_final`.

## Cambios principales

### Seguridad y acceso

- Se restringio el acceso de clientes autenticados para que solo puedan consultar su propio cliente, sus ordenes y sus pagos.
- Se agrego `cedula_persona` al usuario de sesion para soportar validaciones de pertenencia.
- Se mantuvo acceso completo para roles `Administrador` y `Empleado`.

### Bootstrap y configuracion de base de datos

- Se agrego la bandera `BOOTSTRAP_DATABASE` para evitar crear/sembrar la base en cada arranque normal.
- Se adapto la construccion del `SQLALCHEMY_DATABASE_URI` y del bootstrap para funcionar con el driver legacy `SQL Server` de Windows y con drivers modernos.
- Se documento el uso de variables de entorno en el README.

### Compatibilidad con SQL Server

- Se corrigio la validacion de nombre unico de productos para evitar errores del driver ODBC legacy al usar `LOWER(...)`.
- Se hizo tolerante la serializacion de fechas cuando SQL Server devuelve `DATETIME` como texto.
- Se extendio el esquema de la tabla `pago` para almacenar `approve_url`.

### Flujo PayPal Sandbox

- Se evito crear pagos PayPal duplicados para una misma orden cuando existe uno pendiente o aprobado.
- Se hizo idempotente la captura de pagos ya aprobados.
- Se agregaron `return_url` y `cancel_url` al crear ordenes PayPal.
- Se creo la pantalla de retorno `/paypal/retorno` para capturar automaticamente el pago despues de la aprobacion.
- Se agrego un endpoint para capturar por referencia/token de PayPal.
- Se guarda `approve_url` para poder reabrir un pago pendiente.
- Se agrego la capacidad de cancelar pagos pendientes desde la UI para desbloquear la orden y generar un checkout nuevo.
- Si PayPal no devuelve un `approve_url`, el sistema construye un enlace de respaldo con el token de la orden.
- Cuando un pago queda `Aprobado`, la orden pasa automaticamente de `En preparacion` a `Listo para envio o recoleccion`.

### Frontend

- Se mejoro la pantalla de ordenes para mostrar acciones sobre pagos pendientes.
- Se agrego el boton para reabrir aprobacion PayPal.
- Se agrego el boton para cancelar pagos pendientes.
- Se mejoraron los mensajes del flujo para hacer mas claro el paso a paso.

### Git y limpieza

- Se ignoro la carpeta `.vs/` en el `.gitignore`.
- Se limpio `.env.example` para no dejar secretos o datos de prueba incrustados.

## Verificacion realizada

- Se valido sintaxis con `python -m compileall app tests`.
- Se probo el flujo manual de PayPal Sandbox:
  - crear orden
  - crear pago PayPal
  - aprobar con cuenta `Personal` sandbox
  - retorno a la aplicacion
  - captura exitosa
  - pago con estado `Aprobado`

## Notas operativas

- Para probar PayPal Sandbox se requiere:
  - app sandbox con `PAYPAL_CLIENT_ID` y `PAYPAL_CLIENT_SECRET`
  - cuenta sandbox `Business` como vendedor
  - cuenta sandbox `Personal` distinta para aprobar el pago
- Los pagos pendientes creados antes de almacenar `approve_url` pueden quedar sin enlace de reapertura. En esos casos se recomienda cancelarlos desde la UI y generar uno nuevo.
