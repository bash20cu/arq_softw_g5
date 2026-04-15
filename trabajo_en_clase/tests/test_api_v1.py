from app.database import db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User


def _login(client):
    return client.post(
        "/api/v1/auth/verificar",
        json={"username": "miguel_admin", "password": "admin123"},
    )


def test_health_public(client):
    # Esperado: la ruta publica responde OK con JSON minimo de salud.
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_public_catalogs_are_available_without_session(client):
    response = client.get("/api/v1/catalogos/provincias")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_protected_endpoint_requires_session(client):
    # Esperado: middleware de auth bloquea sin cookie de sesion.
    response = client.get("/api/v1/usuario")
    assert response.status_code == 401


def test_auth_verify_success(client):
    # Esperado: login correcto, status 200 y estructura JSON con next + user.
    response = _login(client)
    data = response.get_json()

    assert response.status_code == 200
    assert data["ok"] is True
    assert data["next"] == "/api/v1/menu/principal"
    assert data["user"]["username"] == "miguel_admin"


def test_auth_verify_invalid_credentials(client):
    # Esperado: credenciales invalidas devuelven 401.
    response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "miguel_admin", "password": "bad-password"},
    )
    assert response.status_code == 401


def test_menu_principal_kpis_are_dynamic(client):
    # Esperado: endpoint protegido responde y devuelve KPIs dinamicos.
    _login(client)
    response = client.get("/api/v1/menu/principal")
    data = response.get_json()

    assert response.status_code == 200
    assert data["kpis"]["ordenes_pendientes"] == 2
    assert data["kpis"]["envios_en_ruta"] == 1
    assert data["kpis"]["casos_soporte_abiertos"] == 2


def test_logout_invalidates_session(client):
    # Esperado: logout limpia cookie/sesion y bloquea rutas protegidas.
    _login(client)
    logout_response = client.post("/api/v1/auth/logout")
    menu_response = client.get("/api/v1/menu/principal")

    assert logout_response.status_code == 200
    assert menu_response.status_code == 401


def test_list_users_requires_login_and_returns_data(client):
    # Esperado: lista usuarios responde 200 y JSON array.
    _login(client)
    response = client.get("/api/v1/usuario")
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2


def test_create_user_validates_required_fields(client):
    # Esperado: payload incompleto devuelve 400.
    _login(client)
    response = client.post("/api/v1/usuario", json={"username": "nuevo"})
    assert response.status_code == 400


def test_create_user_validates_id_rol_numeric(client):
    # Esperado: id_rol no numerico devuelve 400.
    _login(client)
    response = client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "404440444",
            "username": "laura_ops",
            "password_hash": "laura123",
            "id_rol": "abc",
            "activo": True,
        },
    )
    assert response.status_code == 400


def test_create_user_success(client):
    # Esperado: insertar usuario valido devuelve 201 y lo serializa en JSON.
    _login(client)
    response = client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "404440444",
            "username": "laura_ops",
            "password_hash": "laura123",
            "id_rol": 2,
            "activo": True,
        },
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["username"] == "laura_ops"
    assert "id_usuario" in data

    with client.application.app_context():
        stored_user = User.query.filter_by(username="laura_ops").first()
        assert stored_user is not None
        assert stored_user.password_hash.startswith(("pbkdf2:", "scrypt:"))


def test_public_register_and_login(client):
    register_response = client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "909990999",
            "nombre": "Nuevo",
            "apellido": "Publico",
            "email": "nuevo_publico_app@enviosg5.com",
            "telefono": "88881111",
            "username": "nuevo_publico",
            "password": "secret123",
            "activo": True,
        },
    )
    assert register_response.status_code == 201
    register_data = register_response.get_json()
    assert register_data["id_rol"] == 4

    login_response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "nuevo_publico", "password": "secret123"},
    )
    assert login_response.status_code == 200


def test_get_user_by_id(client):
    # Esperado: obtener por id devuelve 200 y el usuario correcto.
    _login(client)
    create_response = client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "505550555",
            "username": "qa_user",
            "password_hash": "qa123",
            "id_rol": 2,
            "activo": True,
        },
    )
    user_id = create_response.get_json()["id_usuario"]

    get_response = client.get(f"/api/v1/usuario/{user_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["username"] == "qa_user"


def test_update_user_success(client):
    # Esperado: actualizacion parcial refleja cambios y mantiene estructura JSON.
    _login(client)
    create_response = client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "606660666",
            "username": "before_update",
            "password_hash": "x123",
            "id_rol": 2,
            "activo": True,
        },
    )
    user_id = create_response.get_json()["id_usuario"]

    update_response = client.put(
        f"/api/v1/usuario/{user_id}",
        json={"username": "after_update", "activo": False},
    )
    data = update_response.get_json()

    assert update_response.status_code == 200
    assert data["username"] == "after_update"
    assert data["activo"] is False


def test_update_user_rejects_empty_payload(client):
    # Esperado: PUT sin campos validos devuelve 400.
    _login(client)
    response = client.put("/api/v1/usuario/1", json={})
    assert response.status_code == 400


def test_delete_user_success(client):
    # Esperado: DELETE elimina registro y GET posterior devuelve 404.
    _login(client)
    create_response = client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "707770777",
            "username": "to_delete",
            "password_hash": "x123",
            "id_rol": 2,
            "activo": True,
        },
    )
    user_id = create_response.get_json()["id_usuario"]

    delete_response = client.delete(f"/api/v1/usuario/{user_id}")
    get_response = client.get(f"/api/v1/usuario/{user_id}")

    assert delete_response.status_code == 200
    assert get_response.status_code == 404


def test_products_requires_login(client):
    response = client.get("/api/v1/productos")
    assert response.status_code == 401


def test_list_products_success(client):
    _login(client)
    response = client.get("/api/v1/productos")
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]["nombre"] == "Envio Nacional Estandar"
    assert data[0]["nombre_campania"] == "Promo Envio Express"


def test_list_campaigns_success(client):
    _login(client)
    response = client.get("/api/v1/campanias")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) >= 2
    assert any(item["nombre"] == "Promo Envio Express" for item in data)


def test_create_product_requires_admin_role(client):
    client.post(
        "/api/v1/auth/verificar",
        json={"username": "carlo_ventas", "password": "ventas123"},
    )
    response = client.post(
        "/api/v1/productos",
        json={"nombre": "Caja Plus", "precio_actual": 125.50, "stock": 10},
    )
    assert response.status_code == 403


def test_create_product_success(client):
    _login(client)
    response = client.post(
        "/api/v1/productos",
        json={"nombre": "Caja Plus", "precio_actual": 125.50, "stock": 10, "id_campania": 2},
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["nombre"] == "Caja Plus"
    assert data["nombre_campania"] == "Temporada Escolar"

    with client.application.app_context():
        stored = Product.query.filter_by(nombre="Caja Plus").first()
        assert stored is not None
        assert stored.stock == 10


def test_create_product_rejects_invalid_price(client):
    _login(client)
    response = client.post(
        "/api/v1/productos",
        json={"nombre": "Caja Error", "precio_actual": 0, "stock": 10},
    )
    assert response.status_code == 400


def test_create_campaign_success(client):
    _login(client)
    response = client.post(
        "/api/v1/campanias",
        json={
            "nombre": "Cyber Week",
            "fecha_inicio": "2026-05-01",
            "fecha_fin": "2026-05-15",
            "descripcion": "Campaña promocional de mayo",
        },
    )
    data = response.get_json()
    assert response.status_code == 201
    assert data["nombre"] == "Cyber Week"


def test_create_user_rejects_unknown_persona(client):
    _login(client)
    response = client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "000000000",
            "username": "ghost_user",
            "password_hash": "laura123",
            "id_rol": 2,
            "activo": True,
        },
    )
    assert response.status_code == 400


def test_create_order_success_updates_stock(client):
    client.post(
        "/api/v1/auth/verificar",
        json={"username": "carlo_ventas", "password": "ventas123"},
    )
    response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": 1,
            "detalles": [
                {"id_producto": 1, "cantidad": 2},
                {"id_producto": 3, "cantidad": 1},
            ],
        },
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["estado"] == "Pendiente"
    assert len(data["detalles"]) == 2
    assert data["total"] == 9500.0

    with client.application.app_context():
        order = db.session.get(Order, data["id_orden"])
        product = db.session.get(Product, 1)
        assert order is not None
        assert len(order.detalles) == 2
        assert product.stock == 498


def test_create_order_rejects_insufficient_stock(client):
    client.post(
        "/api/v1/auth/verificar",
        json={"username": "carlo_ventas", "password": "ventas123"},
    )
    response = client.post(
        "/api/v1/ordenes",
        json={"id_cliente": 1, "detalles": [{"id_producto": 2, "cantidad": 9999}]},
    )
    assert response.status_code == 400


def test_get_order_detail_success(client):
    _login(client)
    response = client.get("/api/v1/ordenes/1")
    data = response.get_json()

    assert response.status_code == 200
    assert data["id_orden"] == 1
    assert len(data["detalles"]) == 1


def test_list_catalogs_distritos_success(client):
    _login(client)
    response = client.get("/api/v1/catalogos/distritos")
    data = response.get_json()

    assert response.status_code == 200
    assert data[0]["id_distrito"] == 10101


def test_list_catalogs_filtered_success(client):
    response = client.get("/api/v1/catalogos/cantones?provincia_id=1")
    data = response.get_json()
    assert response.status_code == 200
    assert all(item["id_provincia"] == 1 for item in data)

    response = client.get("/api/v1/catalogos/distritos?canton_id=101")
    data = response.get_json()
    assert response.status_code == 200
    assert all(item["id_canton"] == 101 for item in data)


def test_list_personas_success(client):
    _login(client)
    response = client.get("/api/v1/personas")
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert any(item["cedula"] == "101110111" for item in data)


def test_create_persona_success(client):
    _login(client)
    response = client.post(
        "/api/v1/personas",
        json={
            "cedula": "808880888",
            "nombre": "Persona",
            "apellido": "Nueva",
            "email": "persona_nueva_test@enviosg5.com",
            "telefono": "88889999",
            "id_distrito": 10101,
        },
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["cedula"] == "808880888"


def test_create_persona_rejects_duplicate_email(client):
    _login(client)
    response = client.post(
        "/api/v1/personas",
        json={
            "cedula": "818881888",
            "nombre": "Persona",
            "apellido": "Duplicada",
            "email": "miguel_admin_test@enviosg5.com",
            "id_distrito": 10101,
        },
    )
    assert response.status_code == 409


def test_update_persona_success(client):
    _login(client)
    response = client.put(
        "/api/v1/personas/101110111",
        json={"telefono": "70000000", "nombre": "Miguelito"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["telefono"] == "70000000"
    assert data["nombre"] == "Miguelito"


def test_delete_persona_in_use_returns_conflict(client):
    _login(client)
    response = client.delete("/api/v1/personas/101110111")
    assert response.status_code == 409
