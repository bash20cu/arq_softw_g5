from flask import request
from sqlalchemy.exc import IntegrityError

from app.controllers.user_controller import UserController
from app.database import db
from app.routes.api_authz import ROLE_ADMIN, roles_required
from app.routes.api_helpers import filter_allowed_fields, to_bool
from app.views.user_view import created_user_response, error_response, users_response


def register_user_routes(bp):
    """User administration routes stay isolated from auth and order workflows."""

    @bp.get("/usuario")
    @roles_required(ROLE_ADMIN)
    def list_users():
        users = UserController.list_users()
        return users_response([u.to_dict() for u in users])

    @bp.post("/usuario")
    @roles_required(ROLE_ADMIN)
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
                activo=to_bool(activo),
            )
        except ValueError as exc:
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("cedula_persona o username ya existe / FK invalida", 409)

        return created_user_response(user.to_dict())

    @bp.get("/usuario/<int:user_id>")
    @roles_required(ROLE_ADMIN)
    def get_user(user_id: int):
        user = UserController.get_user_by_id(user_id)
        if user is None:
            return error_response("usuario no encontrado", 404)
        return user.to_dict(), 200

    @bp.put("/usuario/<int:user_id>")
    @roles_required(ROLE_ADMIN)
    def update_user(user_id: int):
        user = UserController.get_user_by_id(user_id)
        if user is None:
            return error_response("usuario no encontrado", 404)

        payload = request.get_json(silent=True) or {}
        allowed_fields = {"cedula_persona", "username", "password_hash", "id_rol", "activo"}
        update_fields = filter_allowed_fields(payload, allowed_fields)
        if "id_rol" in update_fields:
            try:
                update_fields["id_rol"] = int(update_fields["id_rol"])
            except (TypeError, ValueError):
                return error_response("id_rol debe ser numerico", 400)
        if "activo" in update_fields:
            update_fields["activo"] = to_bool(update_fields["activo"])
        if not update_fields:
            return error_response("no hay campos validos para actualizar", 400)

        try:
            updated_user = UserController.update_user(user, **update_fields)
        except ValueError as exc:
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("datos duplicados o FK invalida", 409)

        return updated_user.to_dict(), 200

    @bp.delete("/usuario/<int:user_id>")
    @roles_required(ROLE_ADMIN)
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
