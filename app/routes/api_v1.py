from functools import wraps

from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError

from app.controllers.auth_controller import AuthController
from app.controllers.menu_controller import MenuController
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
    except IntegrityError:
        db.session.rollback()
        return error_response("cedula_persona o username ya existe / FK invalida", 409)

    return created_user_response(user.to_dict())
<<<<<<< HEAD
# Nuevo endpoint de Login
@api_v1_bp.post("/login")
def login():
=======


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
>>>>>>> developer
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return error_response("username y password son obligatorios", 400)

<<<<<<< HEAD
    user = UserController.get_user_by_username(username)
    if not user:
        return error_response("Usuario no encontrado", 404)

    # Aquí deberías usar hashing (ejemplo bcrypt), pero por ahora lo dejamos simple
    if user.password_hash != password:
        return error_response("Contraseña incorrecta", 401)

    return users_response([user.to_dict()])
=======
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
>>>>>>> developer
