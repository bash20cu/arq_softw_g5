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

    refreshed_order = client.get(f"/api/v1/ordenes/{order_id}")
    assert refreshed_order.status_code == 200
    assert refreshed_order.get_json()["estado"] == "Listo para envio o recoleccion"


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


def test_client_cannot_access_another_client_record(client):
    _login_admin(client)

    first_user = client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "505050505",
            "nombre": "Cliente",
            "apellido": "Uno",
            "email": "cliente.uno@test.local",
            "telefono": "88885555",
            "direccion": "Alajuela",
            "username": "cliente_uno",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert first_user.status_code == 201

    second_user = client.post(
        "/api/v1/auth/registro",
        json={
            "cedula_persona": "606060606",
            "nombre": "Cliente",
            "apellido": "Dos",
            "email": "cliente.dos@test.local",
            "telefono": "88886666",
            "direccion": "Heredia",
            "username": "cliente_dos",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert second_user.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    assert clients_response.status_code == 200
    clients = clients_response.get_json()
    foreign_client = next(item for item in clients if item["email"] == "cliente.dos@test.local")

    client.post("/api/v1/auth/logout")
    login_response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "cliente_uno", "password": "cliente123"},
    )
    assert login_response.status_code == 200

    response = client.get(f"/api/v1/clientes/{foreign_client['id_cliente']}")
    assert response.status_code == 403
    assert response.get_json()["error"] == "forbidden"


def test_client_cannot_access_another_clients_order_or_payments(client, monkeypatch):
    _login_admin(client)

    product_response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito Privado",
            "descripcion": "Producto para control de acceso",
            "precio_base": 1000,
            "iva_porcentaje": 13,
            "stock": 10,
            "activo": True,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id_producto"]

    for cedula, email, username in [
        ("707070707", "cliente.tres@test.local", "cliente_tres"),
        ("808080808", "cliente.cuatro@test.local", "cliente_cuatro"),
    ]:
        register_response = client.post(
            "/api/v1/auth/registro",
            json={
                "cedula_persona": cedula,
                "nombre": "Cliente",
                "apellido": username,
                "email": email,
                "telefono": "88887777",
                "direccion": "Cartago",
                "username": username,
                "password": "cliente123",
                "activo": True,
            },
        )
        assert register_response.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    clients = clients_response.get_json()
    foreign_client = next(item for item in clients if item["email"] == "cliente.cuatro@test.local")

    order_response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": foreign_client["id_cliente"],
            "detalles": [{"id_producto": product_id, "cantidad": 1}],
            "estado": "En preparacion",
        },
    )
    assert order_response.status_code == 201
    order_id = order_response.get_json()["id_orden"]

    def fake_create_paypal_order(order, amount, currency):
        from app.database import db
        from app.models.order import Payment

        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa="PAYPAL-ORDER-PRIVATE-001",
            monto=amount,
            estado="Pendiente",
        )
        db.session.add(payment)
        db.session.commit()
        return {
            "payment": payment.to_dict(),
            "paypal_order": {"id": payment.referencia_externa, "status": "CREATED"},
        }

    monkeypatch.setattr(
        "app.controllers.payment_controller.PaymentController.create_paypal_order",
        fake_create_paypal_order,
    )

    payment_response = client.post(f"/api/v1/ordenes/{order_id}/pagos/paypal/crear-orden")
    assert payment_response.status_code == 201

    client.post("/api/v1/auth/logout")
    login_response = client.post(
        "/api/v1/auth/verificar",
        json={"username": "cliente_tres", "password": "cliente123"},
    )
    assert login_response.status_code == 200

    order_access = client.get(f"/api/v1/ordenes/{order_id}")
    assert order_access.status_code == 403

    status_access = client.get(f"/api/v1/ordenes/{order_id}/estado")
    assert status_access.status_code == 403

    payments_access = client.get(f"/api/v1/ordenes/{order_id}/pagos")
    assert payments_access.status_code == 403


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


def test_create_paypal_order_rejects_duplicate_pending_payment(client, monkeypatch):
    _login_admin(client)

    product_response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito Pago Duplicado",
            "descripcion": "Producto para prueba de pago duplicado",
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
            "cedula_persona": "909090909",
            "nombre": "Cliente",
            "apellido": "Pago",
            "email": "cliente.pago@test.local",
            "telefono": "88889999",
            "direccion": "Cartago",
            "username": "cliente_pago",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert register_response.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    clients = clients_response.get_json()
    cliente = next(item for item in clients if item["email"] == "cliente.pago@test.local")

    order_response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": cliente["id_cliente"],
            "detalles": [{"id_producto": product_id, "cantidad": 1}],
            "estado": "En preparacion",
        },
    )
    assert order_response.status_code == 201
    order_id = order_response.get_json()["id_orden"]

    def fake_create_paypal_order(order, amount, currency):
        from app.controllers.payment_controller import PaymentController
        from app.database import db
        from app.models.order import Payment

        existing = PaymentController.get_latest_payment_for_order(order.id_orden, "paypal")
        if existing is not None and existing.estado == "Pendiente":
            raise ValueError("ya existe un pago paypal pendiente para esta orden")

        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa="PAYPAL-ORDER-DUPLICATE-001",
            monto=amount,
            estado="Pendiente",
        )
        db.session.add(payment)
        db.session.commit()
        return {
            "payment": payment.to_dict(),
            "paypal_order": {"id": payment.referencia_externa, "status": "CREATED"},
        }

    monkeypatch.setattr(
        "app.controllers.payment_controller.PaymentController.create_paypal_order",
        fake_create_paypal_order,
    )

    first_response = client.post(f"/api/v1/ordenes/{order_id}/pagos/paypal/crear-orden")
    assert first_response.status_code == 201

    second_response = client.post(f"/api/v1/ordenes/{order_id}/pagos/paypal/crear-orden")
    assert second_response.status_code == 400
    assert "ya existe un pago paypal pendiente" in second_response.get_json()["error"]


def test_capture_paypal_payment_by_reference(client, monkeypatch):
    _login_admin(client)

    product_response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito Referencia PayPal",
            "descripcion": "Producto para captura por referencia",
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
            "cedula_persona": "919191919",
            "nombre": "Cliente",
            "apellido": "Referencia",
            "email": "cliente.referencia@test.local",
            "telefono": "88889998",
            "direccion": "Cartago",
            "username": "cliente_referencia",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert register_response.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    clients = clients_response.get_json()
    cliente = next(item for item in clients if item["email"] == "cliente.referencia@test.local")

    order_response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": cliente["id_cliente"],
            "detalles": [{"id_producto": product_id, "cantidad": 1}],
            "estado": "En preparacion",
        },
    )
    assert order_response.status_code == 201
    order_id = order_response.get_json()["id_orden"]

    def fake_create_paypal_order(order, amount, currency, **kwargs):
        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa="PAYPAL-ORDER-REFERENCE-001",
            monto=amount,
            estado="Pendiente",
        )
        from app.database import db

        db.session.add(payment)
        db.session.commit()
        return {
            "payment": payment.to_dict(),
            "approve_url": "https://example.com/paypal/approve",
            "paypal_order": {
                "id": "PAYPAL-ORDER-REFERENCE-001",
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

    capture_response = client.post(
        "/api/v1/pagos/paypal/capturar-por-referencia",
        json={"reference": "PAYPAL-ORDER-REFERENCE-001"},
    )
    assert capture_response.status_code == 200
    assert capture_response.get_json()["payment"]["estado"] == "Aprobado"

    refreshed_order = client.get(f"/api/v1/ordenes/{order_id}")
    assert refreshed_order.status_code == 200
    assert refreshed_order.get_json()["estado"] == "Listo para envio o recoleccion"


def test_cancel_pending_payment(client, monkeypatch):
    _login_admin(client)

    product_response = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Patito Cancelar Pago",
            "descripcion": "Producto para cancelar pago pendiente",
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
            "cedula_persona": "929292929",
            "nombre": "Cliente",
            "apellido": "Cancelar",
            "email": "cliente.cancelar@test.local",
            "telefono": "88889997",
            "direccion": "Cartago",
            "username": "cliente_cancelar",
            "password": "cliente123",
            "activo": True,
        },
    )
    assert register_response.status_code == 201

    clients_response = client.get("/api/v1/clientes")
    clients = clients_response.get_json()
    cliente = next(item for item in clients if item["email"] == "cliente.cancelar@test.local")

    order_response = client.post(
        "/api/v1/ordenes",
        json={
            "id_cliente": cliente["id_cliente"],
            "detalles": [{"id_producto": product_id, "cantidad": 1}],
            "estado": "En preparacion",
        },
    )
    assert order_response.status_code == 201
    order_id = order_response.get_json()["id_orden"]

    def fake_create_paypal_order(order, amount, currency, **kwargs):
        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa="PAYPAL-ORDER-CANCEL-001",
            approve_url="https://example.com/paypal/approve/cancel",
            monto=amount,
            estado="Pendiente",
        )
        from app.database import db

        db.session.add(payment)
        db.session.commit()
        return {
            "payment": payment.to_dict(),
            "approve_url": payment.approve_url,
            "paypal_order": {
                "id": "PAYPAL-ORDER-CANCEL-001",
                "status": "CREATED",
            },
        }

    monkeypatch.setattr(
        "app.controllers.payment_controller.PaymentController.create_paypal_order",
        fake_create_paypal_order,
    )

    payment_create_response = client.post(
        f"/api/v1/ordenes/{order_id}/pagos/paypal/crear-orden"
    )
    assert payment_create_response.status_code == 201
    payment_id = payment_create_response.get_json()["payment"]["id_pago"]

    cancel_response = client.post(f"/api/v1/pagos/{payment_id}/cancelar")
    assert cancel_response.status_code == 200
    assert cancel_response.get_json()["estado"] == "Cancelado"
