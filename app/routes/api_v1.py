from functools import wraps

from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError

from app.controllers.user_controller import UserController
from app.database import db
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


@api_v1_bp.get("/health")
def health():
    return {"status": "ok"}, 200


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
        user = UserController.create_user(
            cedula_persona=cedula_persona,
            username=username,
            password_hash=password_hash,
            id_rol=int(id_rol),
            activo=_to_bool(activo),
        )
    except IntegrityError:
        db.session.rollback()
        return error_response("cedula_persona o username ya existe / FK invalida", 409)

    return created_user_response(user.to_dict())


@api_v1_bp.post("/auth/verificar")
def verify_user():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return error_response("username y password son obligatorios", 400)

    user = UserController.verify_credentials(username=username, plain_password=password)
    if user is None:
        return error_response("credenciales invalidas", 401)

    session["user"] = {
        "id_usuario": user.id_usuario,
        "username": user.username,
        "id_rol": user.id_rol,
    }

    return {
        "ok": True,
        "message": "usuario verificado",
        "next": "/api/v1/menu/principal",
        "user": user.to_dict(),
    }, 200


@api_v1_bp.post("/auth/logout")
@login_required
def logout_user():
    session.clear()
    return {"ok": True, "message": "sesion cerrada"}, 200


@api_v1_bp.get("/menu/principal")
@login_required
def main_menu():
    user = session["user"]

    return {
        "empresa": "Envios G5",
        "bienvenida": f"Bienvenido, {user['username']}",
        "modulos": [
            {
                "id": "ordenes",
                "nombre": "Ordenes de envio",
                "descripcion": "Crear y dar seguimiento a ordenes activas.",
                "ruta_front": "/principal/ordenes",
            },
            {
                "id": "clientes",
                "nombre": "Clientes",
                "descripcion": "Gestion de clientes y datos de contacto.",
                "ruta_front": "/principal/clientes",
            },
            {
                "id": "campanias",
                "nombre": "Campanias",
                "descripcion": "Promociones y comunicacion comercial.",
                "ruta_front": "/principal/campanias",
            },
            {
                "id": "soporte",
                "nombre": "Soporte",
                "descripcion": "Casos y seguimiento postventa.",
                "ruta_front": "/principal/soporte",
            },
        ],
        "kpis": {
            "ordenes_pendientes": 14,
            "envios_en_ruta": 27,
            "casos_soporte_abiertos": 5,
        },
        "user": user,
    }, 200
