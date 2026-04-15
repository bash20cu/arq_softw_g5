"""Rutas HTTP para creacion, consulta y captura de pagos."""

from decimal import Decimal

from flask import request, url_for

from app.controllers.order_controller import OrderController
from app.controllers.payment_controller import PaymentController
from app.database import db
from app.routes.api_authz import (
    ROLE_ADMIN,
    ROLE_EMPLEADO,
    ensure_order_access,
    login_required,
    roles_required,
)
from app.views.user_view import error_response


def register_payment_routes(bp):
    """Payment routes encapsulate PayPal-specific HTTP flows and callbacks."""

    @bp.get("/ordenes/<int:order_id>/pagos")
    @login_required
    def list_order_payments(order_id: int):
        """Lista los pagos registrados para una orden dada."""

        order = OrderController.get_order_by_id(order_id)
        if order is None:
            return error_response("orden no encontrada", 404)
        try:
            ensure_order_access(order)
        except PermissionError as exc:
            return error_response(str(exc), 403)
        payments = PaymentController.list_payments_for_order(order_id)
        return [payment.to_dict() for payment in payments], 200

    @bp.post("/ordenes/<int:order_id>/pagos/paypal/crear-orden")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def create_paypal_payment(order_id: int):
        """Genera una orden de cobro en PayPal para la orden comercial indicada."""

        order = OrderController.get_order_by_id(order_id)
        if order is None:
            return error_response("orden no encontrada", 404)

        try:
            amount = Decimal(str(OrderController.calculate_total(order))).quantize(Decimal("0.01"))
            payload = PaymentController.create_paypal_order(
                order=order,
                amount=amount,
                currency="USD",
                # The PayPal checkout redirects back here so the browser can finish
                # the capture flow without manually re-entering payment ids.
                return_url=url_for("frontend.paypal_return_page", _external=True),
                cancel_url=url_for("frontend.paypal_cancel_page", _external=True),
            )
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)

        return payload, 201

    @bp.post("/pagos/paypal/capturar-por-referencia")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def capture_payment_by_reference():
        """Captura un pago PayPal usando su token o referencia externa."""

        payload = request.get_json(silent=True) or {}
        reference = (payload.get("reference") or payload.get("token") or "").strip()
        if not reference:
            return error_response("reference es obligatoria", 400)

        payment = PaymentController.get_payment_by_reference(reference)
        if payment is None:
            return error_response("pago no encontrado", 404)

        try:
            response_payload = PaymentController.capture_paypal_order(payment)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)

        return response_payload, 200

    @bp.post("/pagos/<int:payment_id>/cancelar")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def cancel_payment(payment_id: int):
        """Cancela un pago pendiente existente."""

        payment = PaymentController.get_payment_by_id(payment_id)
        if payment is None:
            return error_response("pago no encontrado", 404)

        try:
            canceled = PaymentController.cancel_pending_payment(payment)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)

        return canceled.to_dict(), 200

    @bp.post("/pagos/<int:payment_id>/capturar")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def capture_payment(payment_id: int):
        """Captura un pago pendiente usando el id local del registro."""

        payment = PaymentController.get_payment_by_id(payment_id)
        if payment is None:
            return error_response("pago no encontrado", 404)

        try:
            payload = PaymentController.capture_paypal_order(payment)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)

        return payload, 200
