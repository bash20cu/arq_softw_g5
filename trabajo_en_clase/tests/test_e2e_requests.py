import os

import pytest
import requests


pytestmark = pytest.mark.e2e


@pytest.fixture()
def base_url():
    value = os.getenv("BASE_URL")
    if not value:
        pytest.skip("Define BASE_URL para correr pruebas E2E con requests.")
    return value.rstrip("/")


def test_e2e_auth_menu_logout_flow(base_url):
    # Esperado: flujo usuario real health -> login -> menu -> logout -> bloqueo de menu.
    with requests.Session() as session:
        health = session.get(f"{base_url}/api/v1/health", timeout=10)
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        login = session.post(
            f"{base_url}/api/v1/auth/verificar",
            json={"username": "miguel_admin", "password": "admin123"},
            timeout=10,
        )
        assert login.status_code == 200
        assert login.json()["ok"] is True

        menu = session.get(f"{base_url}/api/v1/menu/principal", timeout=10)
        assert menu.status_code == 200
        menu_json = menu.json()
        assert "kpis" in menu_json
        assert "modulos" in menu_json

        logout = session.post(f"{base_url}/api/v1/auth/logout", timeout=10)
        assert logout.status_code == 200

        menu_after_logout = session.get(f"{base_url}/api/v1/menu/principal", timeout=10)
        assert menu_after_logout.status_code == 401
