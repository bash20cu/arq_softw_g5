import os

import pymysql
import pytest


pytestmark = pytest.mark.integration


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable for tests: {name}")
    return value


def _login(real_client):
    return real_client.post(
        "/api/v1/auth/verificar",
        json={"username": "miguel_admin", "password": "admin123"},
    )


def test_real_login_ok(real_client):
    # Esperado: ruta de auth responde 200, JSON correcto y cookie de sesion activa.
    response = _login(real_client)
    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is True
    assert data["user"]["username"] == "miguel_admin"
    assert "application/json" in response.content_type


def test_real_menu_principal_after_login(real_client):
    # Esperado: middleware permite acceso autenticado y payload incluye KPIs enteros.
    _login(real_client)
    response = real_client.get("/api/v1/menu/principal")
    data = response.get_json()
    assert response.status_code == 200
    assert data["empresa"] == "Envios G5"
    assert isinstance(data["kpis"]["ordenes_pendientes"], int)
    assert isinstance(data["kpis"]["envios_en_ruta"], int)
    assert isinstance(data["kpis"]["casos_soporte_abiertos"], int)


def test_real_crud_usuario_lifecycle(real_client):
    # Esperado: ciclo completo create/get/update/delete sobre DB real.
    _login(real_client)

    create_response = real_client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "404440444",
            "username": "laura_ops_real",
            "password_hash": "laura123",
            "id_rol": 2,
            "activo": True,
        },
    )
    assert create_response.status_code == 201
    user_id = create_response.get_json()["id_usuario"]

    get_response = real_client.get(f"/api/v1/usuario/{user_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["username"] == "laura_ops_real"

    update_response = real_client.put(
        f"/api/v1/usuario/{user_id}",
        json={"username": "laura_ops_real_updated", "activo": False},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["activo"] is False

    delete_response = real_client.delete(f"/api/v1/usuario/{user_id}")
    assert delete_response.status_code == 200

    get_deleted = real_client.get(f"/api/v1/usuario/{user_id}")
    assert get_deleted.status_code == 404


def test_real_logout_blocks_protected(real_client):
    # Esperado: logout invalida sesion/cookie para endpoints protegidos.
    _login(real_client)
    logout_response = real_client.post("/api/v1/auth/logout")
    protected_response = real_client.get("/api/v1/usuario")
    assert logout_response.status_code == 200
    assert protected_response.status_code == 401


def test_real_invalid_login(real_client):
    # Esperado: credenciales invalidas responden 401.
    response = real_client.post(
        "/api/v1/auth/verificar",
        json={"username": "miguel_admin", "password": "invalid"},
    )
    assert response.status_code == 401


def test_real_create_user_validates_relationships_fk(real_client):
    # Esperado: FK invalida (cedula_persona/id_rol inexistentes) devuelve 409.
    _login(real_client)
    response = real_client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "999999999",
            "username": "fk_invalid_user",
            "password_hash": "x123",
            "id_rol": 99,
            "activo": True,
        },
    )
    assert response.status_code == 409


def test_real_public_register_creates_persona_and_user(real_client):
    response = real_client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "80160023",
            "nombre": "Miguel",
            "apellido": "Admin2",
            "email": "miguel_admin2@enviosg5.com",
            "telefono": "88112233",
            "username": "nuevo_no_persona",
            "password": "abc12345",
            "activo": True,
        },
    )
    assert response.status_code == 201

    login_response = real_client.post(
        "/api/v1/auth/verificar",
        json={"username": "nuevo_no_persona", "password": "abc12345"},
    )
    assert login_response.status_code == 200


def test_real_endpoint_writes_user_in_database(real_client):
    # Esperado: POST /usuario escribe realmente en MySQL (verificado por consulta directa).
    _login(real_client)
    username = "db_write_check"
    create_response = real_client.post(
        "/api/v1/usuario",
        json={
            "cedula_persona": "404440444",
            "username": username,
            "password_hash": "x123",
            "id_rol": 2,
            "activo": True,
        },
    )
    assert create_response.status_code == 201

    conn = pymysql.connect(
        host=_require_env("MYSQL_HOST"),
        port=int(_require_env("MYSQL_PORT")),
        user=_require_env("MYSQL_USER"),
        password=_require_env("MYSQL_PASSWORD"),
        database=_require_env("MYSQL_DATABASE"),
        autocommit=True,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM Usuario WHERE username = %s", (username,)
            )
            count = cursor.fetchone()[0]
            assert count == 1
    finally:
        conn.close()
