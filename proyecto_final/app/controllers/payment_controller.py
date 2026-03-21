import base64
import json
import os
import ssl
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from app.database import db
from app.models.order import Order, Payment


class PaymentController:
    ALLOWED_STATES = {"Pendiente", "Aprobado", "Rechazado", "Cancelado", "Error"}

    @staticmethod
    def list_payments_for_order(order_id: int) -> list[Payment]:
        return Payment.query.filter_by(id_orden=order_id).order_by(Payment.id_pago.desc()).all()

    @staticmethod
    def get_payment_by_id(payment_id: int) -> Payment | None:
        return Payment.query.filter_by(id_pago=payment_id).first()

    @staticmethod
    def get_payment_by_reference(reference: str) -> Payment | None:
        return Payment.query.filter_by(referencia_externa=reference).first()

    @staticmethod
    def create_paypal_order(order: Order, amount: Decimal, currency: str) -> dict:
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
            ],
        }

        response = PaymentController._paypal_request(
            method="POST",
            path="/v2/checkout/orders",
            access_token=access_token,
            payload=payload,
        )
        paypal_order_id = response["id"]
        approve_url = PaymentController._extract_approve_url(response)

        payment = Payment(
            id_orden=order.id_orden,
            proveedor="paypal",
            referencia_externa=paypal_order_id,
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
        if payment.proveedor.lower() != "paypal":
            raise ValueError("solo se soporta captura para paypal")
        if not payment.referencia_externa:
            raise ValueError("el pago no tiene referencia externa")

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

        return {
            "payment": payment.to_dict(),
            "paypal_capture": response,
        }

    @staticmethod
    def mark_payment_state(payment: Payment, state: str) -> Payment:
        normalized = (state or "").strip().title()
        if normalized not in PaymentController.ALLOWED_STATES:
            raise ValueError("estado de pago no permitido")
        payment.estado = normalized
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def _get_paypal_access_token() -> str:
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
        return ssl.create_default_context(cafile=certifi.where())

    @staticmethod
    def _extract_approve_url(payload: dict) -> str | None:
        for link in payload.get("links", []):
            if link.get("rel") == "approve":
                return link.get("href")
        return None
