# Postman - Pruebas Backend

## Objetivo

Este documento sirve para probar el backend del `proyecto_final` con Postman sobre el Caso 5 de ProPat S.A.

## Requisitos

- Tener el backend corriendo con `python3.10 run.py`.
- Tener acceso a `http://127.0.0.1:5000`.
- Trabajar con cookies habilitadas en Postman, porque la autenticacion usa sesion.

## Variables sugeridas en Postman

Crear un Environment con estas variables:

- `base_url` = `http://127.0.0.1:5000`
- `admin_username` = `admin`
- `admin_password` = `admin123`
- `cliente_username` = `cliente_demo`
- `cliente_password` = `cliente123`
- `producto_id` = dejar vacio al inicio
- `cliente_id` = dejar vacio al inicio
- `orden_id` = dejar vacio al inicio

## Usuario semilla

El seed del proyecto crea este usuario para pruebas administrativas:

- usuario: `admin`
- password: `admin123`

## Flujo recomendado de pruebas

### 1. Salud del servicio

**GET** `{{base_url}}/api/v1/health`

Respuesta esperada:

```json
{
  "database": "mssql",
  "status": "ok"
}
```

### 2. Login admin

**POST** `{{base_url}}/api/v1/auth/verificar`

Body JSON:

```json
{
  "username": "{{admin_username}}",
  "password": "{{admin_password}}"
}
```

Respuesta esperada:

- `200 OK`
- cookie de sesion guardada por Postman

### 3. Crear producto

**POST** `{{base_url}}/api/v1/productos`

Body JSON:

```json
{
  "nombre": "Patito Clasico Amarillo",
  "descripcion": "Patito de hule para catalogo inicial",
  "fotografia_url": "https://example.com/patito.jpg",
  "color_estilo": "Amarillo clasico",
  "codigo_barras": "750100000001",
  "precio_base": 2500,
  "iva_porcentaje": 13,
  "stock": 25,
  "activo": true
}
```

Guardar el valor de `id_producto` como `producto_id`.

### 4. Registrar cliente publico

**POST** `{{base_url}}/api/v1/auth/registro`

Body JSON:

```json
{
  "cedula_persona": "202020202",
  "nombre": "Cliente",
  "apellido": "Demo",
  "email": "cliente.demo@propat.local",
  "telefono": "88881111",
  "direccion": "Heredia, Costa Rica",
  "username": "{{cliente_username}}",
  "password": "{{cliente_password}}",
  "activo": true
}
```

### 5. Listar clientes

**GET** `{{base_url}}/api/v1/clientes`

Buscar el cliente creado y guardar su `id_cliente` como `cliente_id`.

### 6. Crear orden

**POST** `{{base_url}}/api/v1/ordenes`

Body JSON:

```json
{
  "id_cliente": {{cliente_id}},
  "detalles": [
    {
      "id_producto": {{producto_id}},
      "cantidad": 2
    }
  ],
  "estado": "En preparacion"
}
```

Guardar el valor de `id_orden` como `orden_id`.

### 7. Consultar detalle de orden

**GET** `{{base_url}}/api/v1/ordenes/{{orden_id}}`

Verificar:

- total calculado
- detalle de productos
- estado inicial

### 8. Cambiar estado de orden

**PUT** `{{base_url}}/api/v1/ordenes/{{orden_id}}`

Body JSON:

```json
{
  "estado": "Listo para envio o recoleccion"
}
```

Luego repetir con:

```json
{
  "estado": "Entregado al cliente"
}
```

### 9. Consultar estado de orden

**GET** `{{base_url}}/api/v1/ordenes/{{orden_id}}/estado`

Respuesta esperada:

- `id_orden`
- `estado`
- `fecha_orden`
- `total`

### 10. Logout

**POST** `{{base_url}}/api/v1/auth/logout`

## Flujo de pagos PayPal Sandbox

Para esta parte necesitas agregar en `.env`:

- `PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com`
- `PAYPAL_CLIENT_ID=...`
- `PAYPAL_CLIENT_SECRET=...`

### 11. Crear orden PayPal para una compra

**POST** `{{base_url}}/api/v1/ordenes/{{orden_id}}/pagos/paypal/crear-orden`

Respuesta esperada:

- `payment.id_pago`
- `payment.referencia_externa`
- `paypal_order.id`
- links devueltos por PayPal

Guardar `payment.id_pago` como `payment_id`.

### 12. Listar pagos de una orden

**GET** `{{base_url}}/api/v1/ordenes/{{orden_id}}/pagos`

### 13. Capturar pago PayPal

**POST** `{{base_url}}/api/v1/pagos/{{payment_id}}/capturar`

Respuesta esperada:

- estado del pago actualizado;
- payload de captura de PayPal.

Nota:

La captura real depende de que la orden sandbox exista y sea aprobada en el flujo de PayPal. Para una primera demo de backend, alcanza con verificar que el backend pueda crear la orden PayPal y persistir la referencia externa.

## Flujo alterno de cliente

Despues del registro, se puede probar login del cliente con:

**POST** `{{base_url}}/api/v1/auth/verificar`

```json
{
  "username": "{{cliente_username}}",
  "password": "{{cliente_password}}"
}
```

Luego consultar:

**GET** `{{base_url}}/api/v1/ordenes/{{orden_id}}/estado`

## Errores comunes

- `401 sesion no verificada`: falta login o Postman no guardo la cookie.
- `403 forbidden`: el rol del usuario no tiene permiso para ese endpoint.
- `409`: conflicto por duplicados o claves foraneas.
- `400`: datos invalidos en el body.

## Nota

Si agregas nuevos endpoints, conviene mantener este README actualizado con el orden de prueba real del backend.
