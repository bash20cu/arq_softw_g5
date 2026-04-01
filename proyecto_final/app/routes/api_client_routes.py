from flask import request
from sqlalchemy.exc import IntegrityError

from app.controllers.client_controller import ClientController
from app.database import db
from app.routes.api_authz import (
    ROLE_ADMIN,
    ROLE_EMPLEADO,
    ensure_client_access,
    login_required,
    roles_required,
)
from app.routes.api_helpers import filter_allowed_fields
from app.views.user_view import error_response


def register_client_routes(bp):
    """Client routes stay focused on HTTP concerns and reuse shared auth policies."""

    @bp.get("/clientes")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def list_clientes():
        clientes = ClientController.list_clients()
        return [cliente.to_dict() for cliente in clientes], 200

    @bp.get("/clientes/<int:client_id>")
    @login_required
    def get_cliente(client_id: int):
        cliente = ClientController.get_client_by_id(client_id)
        if cliente is None:
            return error_response("cliente no encontrado", 404)
        try:
            ensure_client_access(cliente)
        except PermissionError as exc:
            return error_response(str(exc), 403)
        return cliente.to_dict(), 200

    @bp.post("/clientes")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def create_cliente():
        payload = request.get_json(silent=True) or {}
        try:
            cliente = ClientController.create_client(
                tipo_cliente=payload.get("tipo_cliente", "Persona"),
                nombre=payload.get("nombre"),
                apellido=payload.get("apellido"),
                email=payload.get("email"),
                telefono=payload.get("telefono"),
                direccion=payload.get("direccion"),
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

    @bp.put("/clientes/<int:client_id>")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def update_cliente(client_id: int):
        cliente = ClientController.get_client_by_id(client_id)
        if cliente is None:
            return error_response("cliente no encontrado", 404)

        payload = request.get_json(silent=True) or {}
        allowed_fields = {
            "cedula_persona",
            "tipo_cliente",
            "nombre",
            "apellido",
            "email",
            "telefono",
            "direccion",
            "id_distrito",
            "puntos_lealtad",
            "estado_cliente",
        }
        update_fields = filter_allowed_fields(payload, allowed_fields)
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

    @bp.delete("/clientes/<int:client_id>")
    @roles_required(ROLE_ADMIN)
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
