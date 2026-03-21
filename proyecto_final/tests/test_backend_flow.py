from app.models.order import Payment


def _login_admin(client):
    response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200


def _register_client_user(client):
    response = client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "303030303",
            "nombre": "Cliente",
            "apellido": "Permisos",
            "email": "cliente.permisos@test.local",
            "telefono": "88883333",
            "direccion": "Alajuela",
            "username": "cliente_perm",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert response.status_code == 201


def _login_client(client):
    response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "cliente_perm", "password": "cliente123"},
    )
    assert response.status_code == 200


def test_full_backend_flow_with_paypal_stub(client, monkeypatch):
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.get_json() == {"status": "ok", "database": "mssql"}

    _login_admin(client)

    product_response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito QA",
            "descripcion": "Producto para flujo de prueba",
            "fotografia_url": "https://example.com/patito-qa.jpg",
            "color_estilo": "Amarillo",
            "codigo_barras": "750100000999",
            "precio_base": 1000,
            "iva_porcentaje": 13,
            "stock": 10,
            "activo": True,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id_producto"]

    register_response = client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "202020202",
            "nombre": "Cliente",
            "apellido": "Demo",
            "email": "cliente.demo@test.local",
            "telefono": "88881111",
            "direccion": "Heredia",
            "username": "cliente_demo",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert register_response.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    assert clients_response.status_code == 200
    clients = clients_response.get_json()
    cliente = next(item for item in clients if item["email"] == "cliente.demo@test.local")
    client_id = cliente["id_cliente"]

    order_response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": client_id,
            "detalles": [
                {
                    "id_producto": product_id,
                    "cantidad": 2,
                }
            ],
            "estado": "En preparacion",
        },
    )
    assert order_response.status_code == 201
    order_payload = order_response.get_json()
    order_id = order_payload["id_orden"]
    assert order_payload["estado"] == "En preparacion"
    assert order_payload["total"] == 2260.0

    status_response = client.get(f"/api/v1/ordenes/{order_id}/estado")
    assert status_response.status_code == 200
    assert status_response.get_json()["estado"] == "En preparacion"

    update_response = client.put(
        f"/api/v1/ordenes/{order_id}",
        json={"estado": "Listo para envio o recoleccion"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["estado"] == "Listo para envio o recoleccion"

    def fake_create_paypal_order(order, amount, currency):
        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa="PAYPAL-ORDER-TEST-001",
            monto=amount,
            estado="Pendiente",
        )
        from app.database import db

        db.session.add(payment)
        db.session.commit()
        return {
            "payment": payment.to_dict(),
            "paypal_order": {
                "id": "PAYPAL-ORDER-TEST-001",
                "status": "CREATED",
            },
        }

    def fake_capture_paypal_order(payment):
        from app.database import db

        payment.estado = "Aprobado"
        db.session.add(payment)
        db.session.commit()
        return {
            "payment": payment.to_dict(),
            "paypal_capture": {
                "id": payment.referencia_externa,
                "status": "COMPLETED",
            },
        }

    monkeypatch.setattr(
        "app.controllers.payment_controller.PaymentController.create_paypal_order",
        fake_create_paypal_order,
    )
    monkeypatch.setattr(
        "app.controllers.payment_controller.PaymentController.capture_paypal_order",
        fake_capture_paypal_order,
    )

    payment_create_response = client.post(
        f"/api/v1/ordenes/{order_id}/pagos/paypal/crear-orden"
    )
    assert payment_create_response.status_code == 201
    payment_payload = payment_create_response.get_json()
    payment_id = payment_payload["payment"]["id_pago"]
    assert payment_payload["payment"]["estado"] == "Pendiente"

    payments_response = client.get(f"/api/v1/ordenes/{order_id}/pagos")
    assert payments_response.status_code == 200
    payments = payments_response.get_json()
    assert len(payments) == 1
    assert payments[0]["referencia_externa"] == "PAYPAL-ORDER-TEST-001"

    capture_response = client.post(f"/api/v1/pagos/{payment_id}/capturar")
    assert capture_response.status_code == 200
    capture_payload = capture_response.get_json()
    assert capture_payload["payment"]["estado"] == "Aprobado"
    assert capture_payload["paypal_capture"]["status"] == "COMPLETED"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "admin", "password": "bad-password"},
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "credenciales invalidas"


def test_protected_route_requires_session(client):
    response = client.get("/api/v1/clientes")
    assert response.status_code == 401
    assert response.get_json()["error"] == "sesion no verificada"


def test_client_role_cannot_create_product(client):
    _register_client_user(client)
    _login_client(client)

    response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito Sin Permiso",
            "precio_base": 1000,
            "iva_porcentaje": 13,
            "stock": 3,
            "activo": True,
        },
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "forbidden"


def test_create_product_validates_required_name_and_price(client):
    _login_admin(client)

    response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "",
            "precio_base": 0,
            "iva_porcentaje": 13,
            "stock": 3,
            "activo": True,
        },
    )
    assert response.status_code == 400
    assert response.get_json()["error"] in {
        "nombre es obligatorio",
        "precio_base debe ser mayor a cero",
    }


def test_create_order_rejects_insufficient_stock(client):
    _login_admin(client)

    product_response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito Stock Limitado",
            "descripcion": "Stock corto para validacion",
            "precio_base": 1500,
            "iva_porcentaje": 13,
            "stock": 1,
            "activo": True,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id_producto"]

    register_response = client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "404040404",
            "nombre": "Cliente",
            "apellido": "Stock",
            "email": "cliente.stock@test.local",
            "telefono": "88884444",
            "direccion": "Cartago",
            "username": "cliente_stock",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert register_response.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    clients = clients_response.get_json()
    cliente = next(item for item in clients if item["email"] == "cliente.stock@test.local")
    client_id = cliente["id_cliente"]

    order_response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": client_id,
            "detalles": [
                {
                    "id_producto": product_id,
                    "cantidad": 2,
                }
            ],
            "estado": "En preparacion",
        },
    )
    assert order_response.status_code == 400
    assert "stock insuficiente" in order_response.get_json()["error"]
