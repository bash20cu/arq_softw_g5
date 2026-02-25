# arq_softw_g5

Estructura base propuesta para un proyecto MVC con Python, MySQL y APIs REST.

## git
https://github.com/bash20cu/arq_softw_g5


## commandos 
python -m venv .venv
.\.venv\Scripts\activate
pip install -r .\requirements.txt


 pruebas de integracion 

  $env:BASE_URL="http://localhost:5000"
  python -m pytest -q -m e2e
  python -m pytest -q





### branch 
- [ ] main intocable , solo para cambios estables ,
- [ ] dev rama developer , solo para hacer los joins estables
- [ ] dev/[devname] - [ fecha] rama independiente para cada uno. 
- [ ] dev/qa parea pruebas necesarias con pytest.



## Tareas 2026-02-17

- [x] Seleccion de arquitectura y stack 
- [x] base de datos 
- [ ] login con autentificacion - brandon
- [X] main menu - menu principal (API)  - Miguel
- [ ] pantalla de inserccion de datos ( CRUD usuario ) - crud de usuarios - Carlos
- 
- 

###  login con autentificacion - brandon 

#### Endpoints API REST (ejemplo)

    - `GET /api/v1/usuario` -> usuario y contraseña con hash  mock de api 
    - `POST /api/v1/usuario` -> crea usuario.
    


### main menu - menu principal (API)  - Miguel

el api, y la entrada completa de la app, con la estructura de carpetas


### pantalla de inserccion de datos ( CRUD usuario ) - crud de usuarios - Carlos 

- `GET /api/v1/usuario` -> lista usuarios.
- `GET /api/v1/usuario/{id}` -> detalle de usuario.
- `POST /api/v1/usuario` -> crea usuario.
- `PUT /api/v1/usuario/{id}` -> actualiza usuario.
- `DELETE /api/v1/usuario/{id}` -> elimina usuario.




## Stack

- Python 3.x 
- Flask -> SSR
- MySQL
- SQLAlchemy

## Estructura MVC + API sugerida

```text
arq_softw_g5/
|- app/
|  |- __init__.py
|  |- config.py
|  |- database.py
|  |- controllers/
|  |  |- __init__.py
|  |  |- user_controller.py
|  |- models/
|  |  |- __init__.py
|  |  |- user.py
|  |- views/
|  |  |- __init__.py
|  |  |- user_view.py
|  |- routes/
|     |- __init__.py
|     |- api_v1.py
|  |- models/
|  |  |- schema.sql
|  |  |- seed.sql
|- tests/
|  |- test_users_api.py
|- .env.example
|- requirements.txt
|- run.py
```

## Rol de cada capa

- Model (`app/models`): representa tablas y reglas de datos.
- Controller (`app/controllers`): contiene la logica de negocio.
- View/API (`app/views` + `app/routes`): expone endpoints REST y respuestas JSON.

## Endpoints API REST (ejemplo)

- `GET /api/v1/users` -> lista usuarios.
- `GET /api/v1/users/{id}` -> detalle de usuario.
- `POST /api/v1/users` -> crea usuario.
- `PUT /api/v1/users/{id}` -> actualiza usuario.
- `DELETE /api/v1/users/{id}` -> elimina usuario.

## Flujo basico

1. La ruta API recibe la peticion HTTP.
2. El controller valida y procesa.
3. El model consulta/guarda en MySQL.
4. La API responde en JSON.

## Proximo paso

Si esta estructura te parece bien, en el siguiente paso te genero todos los archivos con codigo inicial funcionando para esos endpoints.

## Seed de prueba

1. Ejecuta el esquema:
`mysql -u root -p < app/models/schema.sql`

2. Ejecuta datos de prueba:
`mysql -u root -p sistema_ventas < app/models/seed.sql`

Credenciales demo para `POST /api/v1/auth/verificar`:
- `miguel_admin` / `admin123`
- `carla_ventas` / `ventas123`
- `brandon_soporte` / `soporte123`

Nota: en la base de datos las contrasenas se almacenan con hash (no en texto plano).

## Carga automatica al iniciar app

La app valida si existe la base configurada en `MYSQL_DATABASE`.
Si no existe, ejecuta `app/models/schema.sql` y `app/models/seed.sql` una sola vez.
