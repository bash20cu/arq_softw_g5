# arq_softw_g5

Estructura base propuesta para un proyecto MVC con Python, MySQL y APIs REST.

## Stack

- Python 3.x
- Flask
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
|- sql/
|  |- schema.sql
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
