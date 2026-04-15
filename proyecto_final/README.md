## Proyecto final

Esta carpeta se usara para construir la entrega final del equipo 5.

El contenido de `trabajo_en_clase` puede servir como base, pero aqui solo iremos copiando y adaptando lo necesario para mantener una separacion clara.

### Variables de entorno

Configura las variables definidas en `.env.example`.

- `BOOTSTRAP_DATABASE=false` por defecto para evitar que la app intente crear o sembrar la base de datos en cada arranque.
- Usa `BOOTSTRAP_DATABASE=true` solo en entornos controlados de desarrollo o inicializacion.
- En Linux, `MSSQL_DRIVER` debe coincidir con un driver ODBC instalado, por ejemplo `ODBC Driver 18 for SQL Server` o `FreeTDS`. Si `FreeTDS` aparece en `odbcinst -q -d`, verifica que el paquete este instalado y que la libreria `libtdsodbc.so` exista.
- `PAYPAL_CLIENT_ID` y `PAYPAL_CLIENT_SECRET` son obligatorias solo para el flujo real de PayPal.

### Seguridad

- Los clientes autenticados solo pueden consultar sus propios datos, ordenes y pagos.
- Los usuarios con rol Administrador o Empleado mantienen acceso operativo completo.


paypal account sandbox
https://sandbox.paypal.com
sb-4nuk950066529@personal.example.com
5F)#yN-*
