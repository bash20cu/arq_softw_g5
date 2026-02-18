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
