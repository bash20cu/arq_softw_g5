from flask import Blueprint, request
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


@api_v1_bp.get("/health")
def health():
    return {"status": "ok"}, 200


@api_v1_bp.get("/usuario")
def list_users():
    users = UserController.list_users()
    return users_response([u.to_dict() for u in users])


@api_v1_bp.post("/usuario")
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
