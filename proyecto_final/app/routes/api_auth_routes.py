"""Rutas HTTP relacionadas con autenticacion y autorregistro."""

from flask import request, session
from sqlalchemy.exc import IntegrityError

from app.controllers.auth_controller import AuthController
from app.controllers.client_controller import ClientController
from app.controllers.user_controller import UserController
from app.database import db
from app.models.user import Persona
from app.routes.api_authz import ROLE_CLIENTE, login_required
from app.routes.api_helpers import to_bool
from app.views.user_view import created_user_response, error_response


def register_auth_routes(bp):
    """Authentication routes manage session lifecycle and self-service registration."""

    @bp.post("/auth/verificar")
    def verify_user():
        """Inicia sesion validando username y password."""

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

    @bp.post("/auth/registro")
    def register_user():
        """Registra un usuario cliente y crea sus registros base si hacen falta."""

        payload = request.get_json(silent=True) or {}
        cedula_persona = (payload.get("cedula_persona") or "").strip()
        username = (payload.get("username") or "").strip()
        password = payload.get("password")
        nombre = (payload.get("nombre") or "").strip()
        apellido = (payload.get("apellido") or "").strip()
        email = (payload.get("email") or "").strip()
        telefono = (payload.get("telefono") or "").strip() or None
        direccion = (payload.get("direccion") or "").strip() or None
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
            db.session.flush()

        try:
            user = UserController.create_user(
                cedula_persona=cedula_persona,
                username=username,
                password_hash=password,
                id_rol=ROLE_CLIENTE,
                activo=to_bool(activo),
            )
            if ClientController.get_client_by_cedula(cedula_persona) is None:
                ClientController.create_client_from_persona(
                    cedula_persona=cedula_persona,
                    estado_cliente="Activo",
                )
                if direccion:
                    client = ClientController.get_client_by_cedula(cedula_persona)
                    if client is not None:
                        ClientController.update_client(client, direccion=direccion)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("cedula_persona o username ya existe / FK invalida", 409)

        return created_user_response(user.to_dict())

    @bp.post("/auth/logout")
    @login_required
    def logout_user():
        """Cierra la sesion actual del usuario autenticado."""

        session.clear()
        return {"ok": True, "message": "sesion cerrada"}, 200

    @bp.get("/menu/principal")
    @login_required
    def main_menu():
        """Devuelve un menu simple de modulos disponible para el frontend."""

        user = session["user"]
        return {
            "user": user,
            "modulos": [
                {"nombre": "productos", "path": "/api/v1/productos"},
                {"nombre": "clientes", "path": "/api/v1/clientes"},
                {"nombre": "ordenes", "path": "/api/v1/ordenes"},
            ],
        }, 200
