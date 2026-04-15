"""Controlador de pagos.

Orquesta la comunicacion con PayPal, la persistencia de pagos y la
sincronizacion del estado comercial de la orden cuando un cobro se aprueba.
"""

import base64
import json
import os
import ssl
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from app.controllers.order_controller import OrderController
from app.database import db
from app.models.order import Order, Payment


class PaymentController:
    """Gestiona pagos locales y la integracion HTTP con PayPal."""

    ALLOWED_STATES = {"Pendiente", "Aprobado", "Rechazado", "Cancelado", "Error"}

    @staticmethod
    def list_payments_for_order(order_id: int) -> list[Payment]:
        """Lista los pagos de una orden desde el mas reciente al mas antiguo."""

        return Payment.query.filter_by(id_orden=order_id).order_by(Payment.id_pago.desc()).all()

    @staticmethod
    def get_payment_by_id(payment_id: int) -> Payment | None:
        """Busca un pago por su id interno."""

        return Payment.query.filter_by(id_pago=payment_id).first()

    @staticmethod
    def get_payment_by_reference(reference: str) -> Payment | None:
        """Busca un pago usando la referencia externa del proveedor."""

        return Payment.query.filter_by(referencia_externa=reference).first()

    @staticmethod
    def get_latest_payment_for_order(order_id: int, provider: str) -> Payment | None:
        """Obtiene el ultimo pago registrado para una orden y proveedor dados."""

        # We gate new PayPal orders off the latest payment to prevent duplicate
        # pending checkouts for the same order.
        return (
            Payment.query.filter_by(id_orden=order_id, proveedor=provider)
            .order_by(Payment.id_pago.desc())
            .first()
        )

    @staticmethod
    def create_paypal_order(
        order: Order,
        amount: Decimal,
        currency: str,
        *,
        return_url: str | None = None,
        cancel_url: str | None = None,
    ) -> dict:
        """Crea una orden de cobro en PayPal y la registra localmente como pendiente."""

        # Only one active PayPal checkout should exist per order at a time.
        existing_payment = PaymentController.get_latest_payment_for_order(order.id_orden, "paypal")
        if existing_payment is not None:
            if existing_payment.estado == "Pendiente":
                raise ValueError("ya existe un pago paypal pendiente para esta orden")
            if existing_payment.estado == "Aprobado":
                raise ValueError("la orden ya tiene un pago paypal aprobado")

        access_token = PaymentController._get_paypal_access_token()
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(order.id_orden),
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}",
                    },
                    "description": f"Orden ProPat #{order.id_orden}",
                }
            ]
        }
        if return_url and cancel_url:
            payload["payment_source"] = {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": cancel_url,
                    }
                }
            }

        response = PaymentController._paypal_request(
            method="POST",
            path="/v2/checkout/orders",
            access_token=access_token,
            payload=payload,
        )
        paypal_order_id = response["id"]
        # Some PayPal responses omit the approve HATEOAS link; in that case we
        # derive the checkout URL from the order token so the UI can still resume it.
        approve_url = PaymentController._extract_approve_url(response)
        if not approve_url:
            approve_url = PaymentController._build_paypal_approve_url(paypal_order_id)

        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa=paypal_order_id,
            approve_url=approve_url,
            monto=amount,
            estado="Pendiente",
        )
        db.session.add(payment)
        db.session.commit()

        return {
            "payment": payment.to_dict(),
            "approve_url": approve_url,
            "paypal_order": response,
        }

    @staticmethod
    def capture_paypal_order(payment: Payment) -> dict:
        """Captura una orden aprobada de PayPal y actualiza el pago local."""

        if payment.proveedor.lower() != "paypal":
            raise ValueError("solo se soporta captura para paypal")
        if not payment.referencia_externa:
            raise ValueError("el pago no tiene referencia externa")
        # Replaying capture on an already approved payment should be safe/idempotent.
        if payment.estado == "Aprobado":
            return {
                "payment": payment.to_dict(),
                "paypal_capture": {
                    "id": payment.referencia_externa,
                    "status": "COMPLETED",
                    "idempotent": True,
                },
            }
        if payment.estado != "Pendiente":
            raise ValueError("solo se pueden capturar pagos pendientes")

        access_token = PaymentController._get_paypal_access_token()
        response = PaymentController._paypal_request(
            method="POST",
            path=f"/v2/checkout/orders/{payment.referencia_externa}/capture",
            access_token=access_token,
            payload={},
        )

        status = (response.get("status") or "").upper()
        if status == "COMPLETED":
            payment.estado = "Aprobado"
        else:
            payment.estado = "Rechazado"

        db.session.add(payment)
        db.session.commit()
        # Successful payment moves the operational order forward automatically.
        PaymentController._sync_order_after_payment(payment)

        return {
            "payment": payment.to_dict(),
            "paypal_capture": response,
        }

    @staticmethod
    def mark_payment_state(payment: Payment, state: str) -> Payment:
        """Actualiza manualmente el estado de un pago a uno permitido."""

        normalized = (state or "").strip().title()
        if normalized not in PaymentController.ALLOWED_STATES:
            raise ValueError("estado de pago no permitido")
        payment.estado = normalized
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def cancel_pending_payment(payment: Payment) -> Payment:
        """Cancela un pago pendiente para permitir generar uno nuevo."""

        # Cancelling a pending checkout lets the user generate a new PayPal order
        # without mutating the commercial order itself.
        if payment.estado != "Pendiente":
            raise ValueError("solo se pueden cancelar pagos pendientes")
        payment.estado = "Cancelado"
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def _sync_order_after_payment(payment: Payment) -> None:
        """Avanza la orden cuando el pago aprobado la deja lista para entrega."""

        order = payment.orden
        if order is None or payment.estado != "Aprobado":
            return
        if order.estado != "En preparacion":
            return

        OrderController.transition_order(order, "Listo para envio o recoleccion")

    @staticmethod
    def _get_paypal_access_token() -> str:
        """Solicita a PayPal un token OAuth2 para operar contra su API."""

        client_id = os.getenv("PAYPAL_CLIENT_ID", "").strip()
        client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "").strip()
        base_url = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com").strip()

        if not client_id or not client_secret:
            raise ValueError("faltan PAYPAL_CLIENT_ID o PAYPAL_CLIENT_SECRET")

        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode(
            "utf-8"
        )
        body = urlencode({"grant_type": "client_credentials"}).encode("utf-8")
        request = Request(
            url=f"{base_url}/v1/oauth2/token",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        try:
            with urlopen(request, timeout=30, context=PaymentController._ssl_context()) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload["access_token"]
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"paypal auth error: {details}") from exc
        except URLError as exc:
            raise ValueError(f"paypal connection error: {exc.reason}") from exc

    @staticmethod
    def _paypal_request(*, method: str, path: str, access_token: str, payload: dict) -> dict:
        """Ejecuta una peticion autenticada a la API REST de PayPal."""

        base_url = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com").strip()
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            url=f"{base_url}{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=30, context=PaymentController._ssl_context()) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"paypal api error: {details}") from exc
        except URLError as exc:
            raise ValueError(f"paypal connection error: {exc.reason}") from exc

    @staticmethod
    def _ssl_context():
        """Construye el contexto SSL con el certificado raiz actualizado."""

        return ssl.create_default_context(cafile=certifi.where())

    @staticmethod
    def _extract_approve_url(payload: dict) -> str | None:
        """Extrae el enlace de aprobacion de la respuesta HATEOAS de PayPal."""

        for link in payload.get("links", []):
            if link.get("rel") == "approve":
                return link.get("href")
        return None

    @staticmethod
    def _build_paypal_approve_url(reference: str) -> str:
        """Construye una URL de checkout de respaldo a partir del token de PayPal."""

        base_url = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com").strip().lower()
        if "sandbox" in base_url:
            return f"https://www.sandbox.paypal.com/checkoutnow?token={reference}"
        return f"https://www.paypal.com/checkoutnow?token={reference}"
