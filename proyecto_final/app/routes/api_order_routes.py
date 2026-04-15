"""Rutas HTTP para el manejo de ordenes de compra."""

from flask import request, session
from sqlalchemy.exc import IntegrityError

from app.controllers.order_controller import OrderController
from app.database import db
from app.routes.api_authz import (
    ROLE_ADMIN,
    ROLE_EMPLEADO,
    ensure_order_access,
    login_required,
    roles_required,
)
from app.routes.api_helpers import filter_allowed_fields, serialize_order, serialize_order_status
from app.views.user_view import error_response


def register_order_routes(bp):
    """Order routes coordinate CRUD/state transitions and shared access rules."""

    @bp.get("/ordenes")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def list_ordenes():
        """Lista todas las ordenes visibles para personal administrativo."""

        ordenes = OrderController.list_orders()
        return [serialize_order(orden, include_details=False) for orden in ordenes], 200

    @bp.get("/ordenes/<int:order_id>")
    @login_required
    def get_order(order_id: int):
        """Obtiene una orden especifica con todos sus detalles."""

        order = OrderController.get_order_by_id(order_id)
        if order is None:
            return error_response("orden no encontrada", 404)
        try:
            ensure_order_access(order)
        except PermissionError as exc:
            return error_response(str(exc), 403)
        return serialize_order(order, include_details=True), 200

    @bp.get("/ordenes/<int:order_id>/estado")
    @login_required
    def get_order_status(order_id: int):
        """Obtiene solo el estado resumido de una orden."""

        order = OrderController.get_order_by_id(order_id)
        if order is None:
            return error_response("orden no encontrada", 404)
        try:
            ensure_order_access(order)
        except PermissionError as exc:
            return error_response(str(exc), 403)
        return serialize_order_status(order), 200

    @bp.post("/ordenes")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def create_order():
        """Crea una orden nueva y asocia al usuario autenticado que la registra."""

        payload = request.get_json(silent=True) or {}

        try:
            order = OrderController.create_order(
                id_cliente=payload.get("id_cliente"),
                id_usuario=session["user"]["id_usuario"],
                detalles=payload.get("detalles") or [],
                estado=payload.get("estado", "En preparacion"),
            )
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("no fue posible registrar la orden", 409)

        return serialize_order(order, include_details=True), 201

    @bp.put("/ordenes/<int:order_id>")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def update_order(order_id: int):
        """Actualiza una orden o la mueve a otro estado permitido."""

        order = OrderController.get_order_by_id(order_id)
        if order is None:
            return error_response("orden no encontrada", 404)

        payload = request.get_json(silent=True) or {}
        allowed_fields = {"id_cliente", "detalles", "estado"}
        update_fields = filter_allowed_fields(payload, allowed_fields)
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

        return serialize_order(updated, include_details=True), 200

    @bp.post("/ordenes/<int:order_id>/cancelar")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def cancel_order(order_id: int):
        """Cancela una orden usando la logica de negocio del controlador."""

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

        response = serialize_order(canceled, include_details=True)
        response["message"] = "orden cancelada"
        return response, 200
