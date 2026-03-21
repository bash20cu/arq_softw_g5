# Backend testing con Postman (paso a paso)

## 1) Prerrequisitos

- MySQL arriba con `database/docker-compose.yml`.
- Variables en `.env` apuntando a `SistemaVentas`.
- App corriendo con `python run.py`.

Base URL sugerida:
- `http://localhost:5000`

## 2) Cargar base y seed

Ejecuta primero:

```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p SistemaVentas < sql/seed.sql
```

Credenciales de prueba:
- `miguel_admin` / `admin123`
- `carlo_ventas` / `ventas123`
- `brandon_soporte` / `soporte123`

## 3) Configurar Postman

- Crea un Environment con variable `base_url = http://localhost:5000`.
- Activa cookies para conservar sesion (`session`) entre requests.
- En requests JSON usa header:
  - `Content-Type: application/json`

## 4) Prueba de salud

### GET `{{base_url}}/api/v1/health`

Esperado: `200`

```json
{ "status": "ok" }
```

## 5) Login / verificacion de usuario

### POST `{{base_url}}/api/v1/auth/verificar`

Body:

```json
{
  "username": "miguel_admin",
  "password": "admin123"
}
```

Esperado: `200` con `ok: true` y cookie de sesion.

## 6) Menu principal (protegido)

### GET `{{base_url}}/api/v1/menu/principal`

Esperado: `200` con:
- `empresa`
- `modulos`
- `kpis` (conteos reales de DB)
- `user`

## 7) CRUD Usuario

## 7.1 Listar usuarios

### GET `{{base_url}}/api/v1/usuario`

Esperado: `200` con array de usuarios.

## 7.2 Crear usuario

### POST `{{base_url}}/api/v1/usuario`

Usa una persona que exista y no tenga usuario. En seed viene:
- `cedula_persona = 404440444`

Body:

```json
{
  "cedula_persona": "404440444",
  "username": "laura_ops",
  "password_hash": "laura123",
  "id_rol": 2,
  "activo": true
}
```

Esperado: `201`.
Guarda el `id_usuario` para los pasos siguientes.

## 7.3 Obtener usuario por id

### GET `{{base_url}}/api/v1/usuario/{id_usuario}`

Esperado: `200`.

## 7.4 Actualizar usuario

### PUT `{{base_url}}/api/v1/usuario/{id_usuario}`

Body ejemplo:

```json
{
  "username": "laura_operaciones",
  "activo": false
}
```

Esperado: `200` con datos actualizados.

## 7.5 Eliminar usuario

### DELETE `{{base_url}}/api/v1/usuario/{id_usuario}`

Esperado: `200` con `ok: true`.

Nota: si el usuario tiene referencias en otras tablas puede devolver `409`.

## 8) Logout

### POST `{{base_url}}/api/v1/auth/logout`

Esperado: `200`.

Luego prueba de nuevo:
- `GET /api/v1/menu/principal` -> debe devolver `401`.

## 9) Casos de error recomendados

- Login invalido -> `401`.
- Crear usuario sin campos requeridos -> `400`.
- Crear usuario duplicado o FK invalida -> `409`.
- Llamar endpoint protegido sin sesion -> `401`.
