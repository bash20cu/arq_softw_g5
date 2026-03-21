from functools import wraps

from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError

from app.controllers.auth_controller import AuthController
from app.controllers.campaign_controller import CampaignController
from app.controllers.client_controller import ClientController
from app.controllers.menu_controller import MenuController
from app.controllers.order_controller import OrderController
from app.controllers.persona_controller import PersonaController
from app.controllers.product_controller import ProductController
from app.controllers.user_controller import UserController
from app.database import db
from app.models.user import Cliente, Factura, Persona
from app.views.user_view import created_user_response, error_response, users_response

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "si", "yes"}
    return bool(value)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("user") is None:
            return error_response("sesion no verificada", 401)
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if user is None:
                return error_response("sesion no verificada", 401)
            if user.get("id_rol") not in allowed_roles:
                return error_response("forbidden", 403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@api_v1_bp.get("/health")
def health():
    return {"status": "ok"}, 200


@api_v1_bp.get("/clientes")
@login_required
def list_clientes():
    clientes = ClientController.list_clients()
    return [cliente.to_dict() for cliente in clientes], 200


@api_v1_bp.post("/clientes")
@roles_required(1, 2)
def create_cliente():
    payload = request.get_json(silent=True) or {}
    try:
        cliente = ClientController.create_client(
            nombre=payload.get("nombre"),
            apellido=payload.get("apellido"),
            email=payload.get("email"),
            telefono=payload.get("telefono"),
            id_distrito=payload.get("id_distrito"),
            cedula_persona=payload.get("cedula_persona"),
            puntos_lealtad=payload.get("puntos_lealtad", 0),
            estado_cliente=payload.get("estado_cliente", "Activo"),
        )
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible registrar el cliente", 409)
    return cliente.to_dict(), 201


@api_v1_bp.get("/clientes/<int:client_id>")
@login_required
def get_cliente(client_id: int):
    cliente = ClientController.get_client_by_id(client_id)
    if cliente is None:
        return error_response("cliente no encontrado", 404)
    return cliente.to_dict(), 200


@api_v1_bp.put("/clientes/<int:client_id>")
@roles_required(1, 2)
def update_cliente(client_id: int):
    cliente = ClientController.get_client_by_id(client_id)
    if cliente is None:
        return error_response("cliente no encontrado", 404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = {
        "cedula_persona",
        "nombre",
        "apellido",
        "email",
        "telefono",
        "id_distrito",
        "puntos_lealtad",
        "estado_cliente",
    }
    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}
    if not update_fields:
        return error_response("no hay campos validos para actualizar", 400)

    try:
        cliente = ClientController.update_client(cliente, **update_fields)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible actualizar el cliente", 409)

    return cliente.to_dict(), 200


@api_v1_bp.delete("/clientes/<int:client_id>")
@roles_required(1, 2)
def delete_cliente(client_id: int):
    cliente = ClientController.get_client_by_id(client_id)
    if cliente is None:
        return error_response("cliente no encontrado", 404)
    try:
        ClientController.delete_client(cliente)
    except IntegrityError:
        db.session.rollback()
        return error_response("cliente en uso por otras tablas", 409)
    return {"ok": True, "message": "cliente eliminado"}, 200


@api_v1_bp.get("/ordenes")
@login_required
def list_ordenes():
    ordenes = OrderController.list_orders()
    return (
        [
            {
                "id_orden": o.id_orden,
                "id_cliente": o.id_cliente,
                "id_usuario": o.id_usuario,
                "fecha_orden": o.fecha_orden.isoformat() if o.fecha_orden else None,
                "estado": o.estado,
                "total": OrderController.calculate_total(o),
            }
            for o in ordenes
        ],
        200,
    )


@api_v1_bp.get("/campanias")
@login_required
def list_campaigns():
    campanias = CampaignController.list_campaigns()
    return [campania.to_dict() for campania in campanias], 200


@api_v1_bp.get("/campanias/<int:campaign_id>")
@login_required
def get_campaign(campaign_id: int):
    campaign = CampaignController.get_campaign_by_id(campaign_id)
    if campaign is None:
        return error_response("campania no encontrada", 404)
    return campaign.to_dict(), 200


@api_v1_bp.post("/campanias")
@roles_required(1)
def create_campaign():
    payload = request.get_json(silent=True) or {}
    try:
        campania = CampaignController.create_campaign(
            nombre=payload.get("nombre"),
            fecha_inicio=payload.get("fecha_inicio"),
            fecha_fin=payload.get("fecha_fin"),
            descripcion=payload.get("descripcion"),
        )
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible registrar la campania", 409)
    return campania.to_dict(), 201


@api_v1_bp.put("/campanias/<int:campaign_id>")
@roles_required(1)
def update_campaign(campaign_id: int):
    campaign = CampaignController.get_campaign_by_id(campaign_id)
    if campaign is None:
        return error_response("campania no encontrada", 404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = {"nombre", "fecha_inicio", "fecha_fin", "descripcion"}
    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}
    if not update_fields:
        return error_response("no hay campos validos para actualizar", 400)

    try:
        updated = CampaignController.update_campaign(campaign, **update_fields)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible actualizar la campania", 409)
    return updated.to_dict(), 200


@api_v1_bp.delete("/campanias/<int:campaign_id>")
@roles_required(1)
def delete_campaign(campaign_id: int):
    campaign = CampaignController.get_campaign_by_id(campaign_id)
    if campaign is None:
        return error_response("campania no encontrada", 404)
    try:
        CampaignController.delete_campaign(campaign)
    except IntegrityError:
        db.session.rollback()
        return error_response("campania en uso por otras tablas", 409)
    return {"ok": True, "message": "campania eliminada"}, 200


@api_v1_bp.get("/catalogos/roles")
def list_roles():
    return [role.to_dict() for role in PersonaController.list_roles()], 200


@api_v1_bp.get("/catalogos/provincias")
def list_provincias():
    return [provincia.to_dict() for provincia in PersonaController.list_provincias()], 200


@api_v1_bp.get("/catalogos/cantones")
def list_cantones():
    provincia_id = request.args.get("provincia_id", type=int)
    return [canton.to_dict() for canton in PersonaController.list_cantones(provincia_id)], 200


@api_v1_bp.get("/catalogos/distritos")
def list_distritos():
    canton_id = request.args.get("canton_id", type=int)
    return [distrito.to_dict() for distrito in PersonaController.list_distritos(canton_id)], 200


@api_v1_bp.get("/personas")
@login_required
def list_personas():
    personas = PersonaController.list_personas()
    return [persona.to_dict() for persona in personas], 200


@api_v1_bp.post("/personas")
@roles_required(1)
def create_persona():
    payload = request.get_json(silent=True) or {}
    try:
        persona = PersonaController.create_persona(
            cedula=payload.get("cedula"),
            nombre=payload.get("nombre"),
            apellido=payload.get("apellido"),
            email=payload.get("email"),
            telefono=payload.get("telefono"),
            id_distrito=payload.get("id_distrito"),
        )
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("cedula o email ya existe / FK invalida", 409)
    return persona.to_dict(), 201


@api_v1_bp.get("/personas/<string:cedula>")
@login_required
def get_persona(cedula: str):
    persona = PersonaController.get_persona_by_cedula(cedula)
    if persona is None:
        return error_response("persona no encontrada", 404)
    return persona.to_dict(), 200


@api_v1_bp.put("/personas/<string:cedula>")
@roles_required(1)
def update_persona(cedula: str):
    persona = PersonaController.get_persona_by_cedula(cedula)
    if persona is None:
        return error_response("persona no encontrada", 404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = {"nombre", "apellido", "email", "telefono", "id_distrito"}
    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}
    if not update_fields:
        return error_response("no hay campos validos para actualizar", 400)

    try:
        persona = PersonaController.update_persona(persona, **update_fields)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("email ya existe / FK invalida", 409)

    return persona.to_dict(), 200


@api_v1_bp.delete("/personas/<string:cedula>")
@roles_required(1)
def delete_persona(cedula: str):
    persona = PersonaController.get_persona_by_cedula(cedula)
    if persona is None:
        return error_response("persona no encontrada", 404)

    try:
        PersonaController.delete_persona(persona)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 409)
    except IntegrityError:
        db.session.rollback()
        return error_response("persona en uso por otras tablas", 409)
    return {"ok": True, "message": "persona eliminada"}, 200


@api_v1_bp.get("/ordenes/<int:order_id>")
@login_required
def get_order(order_id: int):
    order = OrderController.get_order_by_id(order_id)
    if order is None:
        return error_response("orden no encontrada", 404)

    payload = order.to_dict(include_details=True)
    payload["total"] = OrderController.calculate_total(order)
    return payload, 200


@api_v1_bp.post("/ordenes")
@roles_required(1, 2)
def create_order():
    payload = request.get_json(silent=True) or {}

    try:
        order = OrderController.create_order(
            id_cliente=payload.get("id_cliente"),
            id_usuario=session["user"]["id_usuario"],
            detalles=payload.get("detalles") or [],
            estado=payload.get("estado", "Pendiente"),
        )
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible registrar la orden", 409)

    response = order.to_dict(include_details=True)
    response["total"] = OrderController.calculate_total(order)
    return response, 201


@api_v1_bp.put("/ordenes/<int:order_id>")
@roles_required(1, 2)
def update_order(order_id: int):
    order = OrderController.get_order_by_id(order_id)
    if order is None:
        return error_response("orden no encontrada", 404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = {"id_cliente", "detalles", "estado"}
    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}
    if not update_fields:
        return error_response("no hay campos validos para actualizar", 400)

    try:
        updated = OrderController.update_order(order, **update_fields)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible actualizar la orden", 409)

    response = updated.to_dict(include_details=True)
    response["total"] = OrderController.calculate_total(updated)
    return response, 200


@api_v1_bp.post("/ordenes/<int:order_id>/cancelar")
@roles_required(1, 2)
def cancel_order(order_id: int):
    order = OrderController.get_order_by_id(order_id)
    if order is None:
        return error_response("orden no encontrada", 404)

    try:
        canceled = OrderController.cancel_order(order)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("no fue posible cancelar la orden", 409)

    response = canceled.to_dict(include_details=True)
    response["total"] = OrderController.calculate_total(canceled)
    response["message"] = "orden cancelada"
    return response, 200


@api_v1_bp.get("/facturas")
@login_required
def list_facturas():
    facturas = Factura.query.all()
    return (
        [
            {
                "id_factura": f.id_factura,
                "numero_factura": f.numero_factura,
                "monto_total": f.monto_total,
                "fecha_emision": f.fecha_emision.isoformat() if f.fecha_emision else None,
            }
            for f in facturas
        ],
        200,
    )


@api_v1_bp.get("/productos")
@login_required
def list_products():
    products = ProductController.list_products()
    return [product.to_dict() for product in products], 200


@api_v1_bp.post("/productos")
@roles_required(1)
def create_product():
    payload = request.get_json(silent=True) or {}
    try:
        product = ProductController.create_product(
            nombre=payload.get("nombre"),
            precio_actual=payload.get("precio_actual"),
            stock=payload.get("stock"),
            id_campania=payload.get("id_campania"),
        )
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("campania invalida o datos duplicados", 409)

    return product.to_dict(), 201


@api_v1_bp.get("/productos/<int:product_id>")
@login_required
def get_product(product_id: int):
    product = ProductController.get_product_by_id(product_id)
    if product is None:
        return error_response("producto no encontrado", 404)
    return product.to_dict(), 200


@api_v1_bp.put("/productos/<int:product_id>")
@roles_required(1)
def update_product(product_id: int):
    product = ProductController.get_product_by_id(product_id)
    if product is None:
        return error_response("producto no encontrado", 404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = {"nombre", "precio_actual", "stock", "id_campania"}
    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}
    if not update_fields:
        return error_response("no hay campos validos para actualizar", 400)

    try:
        updated = ProductController.update_product(product, **update_fields)
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("campania invalida", 409)

    return updated.to_dict(), 200


@api_v1_bp.delete("/productos/<int:product_id>")
@roles_required(1)
def delete_product(product_id: int):
    product = ProductController.get_product_by_id(product_id)
    if product is None:
        return error_response("producto no encontrado", 404)

    try:
        ProductController.delete_product(product)
    except IntegrityError:
        db.session.rollback()
        return error_response("producto en uso por otras tablas", 409)

    return {"ok": True, "message": "producto eliminado"}, 200


@api_v1_bp.get("/usuario")
@login_required
def list_users():
    users = UserController.list_users()
    return users_response([u.to_dict() for u in users])


@api_v1_bp.post("/usuario")
@login_required
def create_user():
    payload = request.get_json(silent=True) or {}
    cedula_persona = payload.get("cedula_persona")
    username = payload.get("username")
    password_hash = payload.get("password_hash")
    id_rol = payload.get("id_rol")
    activo = payload.get("activo", True)

    if not cedula_persona or not username or not password_hash or not id_rol:
        return error_response(
            "cedula_persona, username, password_hash e id_rol son obligatorios", 400
        )

    try:
        id_rol_value = int(id_rol)
    except (TypeError, ValueError):
        return error_response("id_rol debe ser numerico", 400)

    try:
        user = UserController.create_user(
            cedula_persona=cedula_persona,
            username=username,
            password_hash=password_hash,
            id_rol=id_rol_value,
            activo=_to_bool(activo),
        )
    except ValueError as exc:
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("cedula_persona o username ya existe / FK invalida", 409)

    return created_user_response(user.to_dict())


@api_v1_bp.get("/usuario/<int:user_id>")
@login_required
def get_user(user_id: int):
    user = UserController.get_user_by_id(user_id)
    if user is None:
        return error_response("usuario no encontrado", 404)
    return user.to_dict(), 200


@api_v1_bp.put("/usuario/<int:user_id>")
@login_required
def update_user(user_id: int):
    user = UserController.get_user_by_id(user_id)
    if user is None:
        return error_response("usuario no encontrado", 404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = {"cedula_persona", "username", "password_hash", "id_rol", "activo"}
    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}

    if not update_fields:
        return error_response("no hay campos validos para actualizar", 400)

    if "id_rol" in update_fields:
        try:
            update_fields["id_rol"] = int(update_fields["id_rol"])
        except (TypeError, ValueError):
            return error_response("id_rol debe ser numerico", 400)

    if "activo" in update_fields:
        update_fields["activo"] = _to_bool(update_fields["activo"])

    try:
        updated_user = UserController.update_user(user, **update_fields)
    except ValueError as exc:
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("datos duplicados o FK invalida", 409)

    return updated_user.to_dict(), 200


@api_v1_bp.delete("/usuario/<int:user_id>")
@login_required
def delete_user(user_id: int):
    user = UserController.get_user_by_id(user_id)
    if user is None:
        return error_response("usuario no encontrado", 404)

    try:
        UserController.delete_user(user)
    except IntegrityError:
        db.session.rollback()
        return error_response("usuario en uso por otras tablas", 409)

    return {"ok": True, "message": "usuario eliminado"}, 200


@api_v1_bp.post("/auth/verificar")
def verify_user():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return error_response("username y password son obligatorios", 400)

    user = AuthController.verify_credentials(username=username, password=password)
    if user is None:
        return error_response("credenciales invalidas", 401)

    session["user"] = AuthController.build_session_user(user)

    return {
        "ok": True,
        "message": "usuario verificado",
        "next": "/api/v1/menu/principal",
        "user": user.to_dict(),
    }, 200


@api_v1_bp.post("/auth/registro")
def register_user():
    payload = request.get_json(silent=True) or {}
    cedula_persona = (payload.get("cedula_persona") or "").strip()
    username = (payload.get("username") or "").strip()
    password = payload.get("password")
    nombre = (payload.get("nombre") or "").strip()
    apellido = (payload.get("apellido") or "").strip()
    email = (payload.get("email") or "").strip()
    telefono = (payload.get("telefono") or "").strip() or None
    id_distrito = payload.get("id_distrito")
    activo = payload.get("activo", True)

    if not cedula_persona or not username or not password:
        return error_response("cedula_persona, username y password son obligatorios", 400)

    if UserController.get_user_by_username(username) is not None:
        return error_response("username ya existe", 409)

    if UserController.get_user_by_cedula(cedula_persona) is not None:
        return error_response("ya existe un usuario para esa cedula_persona", 409)

    persona = Persona.query.filter_by(cedula=cedula_persona).first()
    if persona is None:
        if not nombre or not apellido or not email:
            return error_response(
                "si la cedula no existe en Persona debes enviar nombre, apellido y email",
                400,
            )

        if Persona.query.filter_by(email=email).first() is not None:
            return error_response("email ya existe en Persona", 409)

        persona = Persona(
            cedula=cedula_persona,
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            id_distrito=id_distrito,
        )
        db.session.add(persona)

    # Registro publico: siempre inicia como Cliente.
    id_rol_value = 4

    try:
        user = UserController.create_user(
            cedula_persona=cedula_persona,
            username=username,
            password_hash=password,
            id_rol=id_rol_value,
            activo=_to_bool(activo),
        )
        if ClientController.get_client_by_cedula(cedula_persona) is None:
            ClientController.create_client_from_persona(
                cedula_persona=cedula_persona,
                estado_cliente="Activo",
            )
    except ValueError as exc:
        db.session.rollback()
        return error_response(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response("cedula_persona o username ya existe / FK invalida", 409)

    return created_user_response(user.to_dict())


@api_v1_bp.post("/auth/logout")
@login_required
def logout_user():
    session.clear()
    return {"ok": True, "message": "sesion cerrada"}, 200


@api_v1_bp.get("/menu/principal")
@login_required
def main_menu():
    user = session["user"]
    return MenuController.get_main_menu_payload(user), 200
