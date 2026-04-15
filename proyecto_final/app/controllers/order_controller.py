"""Controlador de ordenes de compra.

Administra la creacion de ordenes, sus detalles, transiciones de estado y el
ajuste del inventario asociado a cada movimiento.
"""

from decimal import Decimal

from app.database import db
from app.models.order import Order, OrderDetail
from app.models.product import Product
from app.models.user import Cliente


class OrderController:
    """Encapsula la logica de negocio del ciclo de vida de las ordenes."""

    ALLOWED_STATES = {
        "En preparacion",
        "Listo para envio o recoleccion",
        "Entregado al cliente",
        "Cancelado",
    }
    EDITABLE_STATES = {"En preparacion"}
    TRANSITIONS = {
        "En preparacion": {"Listo para envio o recoleccion", "Cancelado"},
        "Listo para envio o recoleccion": {"Entregado al cliente", "Cancelado"},
        "Entregado al cliente": set(),
        "Cancelado": set(),
    }

    @staticmethod
    def list_orders() -> list[Order]:
        """Lista las ordenes desde la mas reciente hasta la mas antigua."""

        return Order.query.order_by(Order.id_orden.desc()).all()

    @staticmethod
    def get_order_by_id(order_id: int) -> Order | None:
        """Busca una orden por su identificador."""

        return Order.query.filter_by(id_orden=order_id).first()

    @staticmethod
    def create_order(
        *,
        id_cliente,
        id_usuario,
        detalles: list[dict],
        estado: str = "En preparacion",
    ) -> Order:
        """Crea una orden, valida sus detalles y descuenta inventario."""

        cliente_id = OrderController._validate_cliente(id_cliente)
        usuario_id = OrderController._validate_positive_int(id_usuario, "id_usuario")
        normalized_state = OrderController._validate_state(estado)
        normalized_details = OrderController._validate_detalles(detalles)

        order = Order(
            id_cliente=cliente_id,
            id_usuario=usuario_id,
            estado=normalized_state,
        )
        db.session.add(order)
        db.session.flush()

        for item in normalized_details:
            product = item["product"]
            product.stock -= item["cantidad"]
            detail = OrderDetail(
                id_orden=order.id_orden,
                id_producto=product.id_producto,
                cantidad=item["cantidad"],
                precio_venta=item["precio_venta"],
            )
            db.session.add(detail)

        db.session.commit()
        return OrderController.get_order_by_id(order.id_orden)

    @staticmethod
    def update_order(
        order: Order,
        *,
        id_cliente=None,
        detalles: list[dict] | None = None,
        estado: str | None = None,
    ) -> Order:
        """Actualiza una orden existente respetando sus restricciones de estado."""

        if (id_cliente is not None or detalles is not None) and order.estado not in OrderController.EDITABLE_STATES:
            raise ValueError("solo se pueden editar datos de una orden en preparacion")

        if id_cliente is not None:
            order.id_cliente = OrderController._validate_cliente(id_cliente)

        if detalles is not None:
            normalized_details = OrderController._validate_updated_detalles(order, detalles)
            OrderController._replace_order_details(order, normalized_details)

        if estado is not None:
            normalized_state = OrderController._validate_state(estado)
            if normalized_state != order.estado:
                order = OrderController.transition_order(order, normalized_state)
                if id_cliente is None and detalles is None:
                    return order

        db.session.add(order)
        db.session.commit()
        return OrderController.get_order_by_id(order.id_orden)

    @staticmethod
    def cancel_order(order: Order) -> Order:
        """Cancela una orden y devuelve stock cuando corresponde."""

        if order.estado == "Cancelado":
            return OrderController.get_order_by_id(order.id_orden)
        if "Cancelado" not in OrderController.TRANSITIONS.get(order.estado, set()):
            raise ValueError("la orden ya no se puede cancelar en este estado")
        if order.estado in OrderController.EDITABLE_STATES:
            OrderController._restore_order_stock(order)
        order.estado = "Cancelado"
        db.session.add(order)
        db.session.commit()
        return OrderController.get_order_by_id(order.id_orden)

    @staticmethod
    def transition_order(order: Order, next_state: str) -> Order:
        """Mueve la orden a un nuevo estado permitido por la matriz de transiciones."""

        next_state = OrderController._validate_state(next_state)
        if next_state == order.estado:
            return OrderController.get_order_by_id(order.id_orden)
        if next_state == "Cancelado":
            return OrderController.cancel_order(order)

        allowed = OrderController.TRANSITIONS.get(order.estado, set())
        if next_state not in allowed:
            raise ValueError(f"no se puede pasar de {order.estado} a {next_state}")

        order.estado = next_state
        db.session.add(order)
        db.session.commit()
        return OrderController.get_order_by_id(order.id_orden)

    @staticmethod
    def get_available_transitions(order: Order) -> list[str]:
        """Devuelve los siguientes estados permitidos para una orden."""

        return sorted(OrderController.TRANSITIONS.get(order.estado, set()))

    @staticmethod
    def calculate_total(order: Order) -> float:
        """Calcula el total monetario de una orden sumando sus detalles."""

        return float(
            sum(Decimal(str(detalle.precio_venta)) * detalle.cantidad for detalle in order.detalles)
        )

    @staticmethod
    def _validate_cliente(value) -> int:
        """Valida que el cliente exista y devuelve su id normalizado."""

        cliente_id = OrderController._validate_positive_int(value, "id_cliente")
        cliente = Cliente.query.filter_by(id_cliente=cliente_id).first()
        if cliente is None:
            raise ValueError("cliente no existe")
        return cliente_id

    @staticmethod
    def _validate_positive_int(value, field_name: str) -> int:
        """Valida enteros positivos usados como ids y cantidades."""

        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} debe ser numerico") from exc
        if parsed <= 0:
            raise ValueError(f"{field_name} debe ser mayor a cero")
        return parsed

    @staticmethod
    def _validate_state(value: str) -> str:
        """Valida que el estado solicitado exista en el flujo permitido."""

        state = (value or "En preparacion").strip()
        if state not in OrderController.ALLOWED_STATES:
            raise ValueError("estado no permitido")
        return state

    @staticmethod
    def _validate_detalles(items: list[dict]) -> list[dict]:
        """Valida los detalles de una orden y comprueba stock disponible."""

        if not items:
            raise ValueError("detalles es obligatorio")

        normalized = []
        for item in items:
            product_id = OrderController._validate_positive_int(
                item.get("id_producto"), "id_producto"
            )
            cantidad = OrderController._validate_positive_int(
                item.get("cantidad"), "cantidad"
            )
            product = Product.query.filter_by(id_producto=product_id).first()
            if product is None:
                raise ValueError(f"producto {product_id} no existe")
            if product.stock < cantidad:
                raise ValueError(f"stock insuficiente para producto {product_id}")

            normalized.append(
                {
                    "product": product,
                    "cantidad": cantidad,
                    "precio_venta": Decimal(str(product.precio_actual)).quantize(
                        Decimal("0.01")
                    ),
                }
            )

        return normalized

    @staticmethod
    def _validate_updated_detalles(order: Order, items: list[dict]) -> list[dict]:
        """Restaura stock previo y luego valida los nuevos detalles de la orden."""

        OrderController._restore_order_stock(order)
        return OrderController._validate_detalles(items)

    @staticmethod
    def _restore_order_stock(order: Order) -> None:
        """Devuelve al inventario las cantidades reservadas por la orden."""

        for detail in order.detalles:
            if detail.producto is not None:
                detail.producto.stock += detail.cantidad

    @staticmethod
    def _replace_order_details(order: Order, items: list[dict]) -> None:
        """Reemplaza todos los detalles de una orden por una nueva coleccion."""

        for detail in list(order.detalles):
            db.session.delete(detail)
        order.detalles.clear()
        db.session.flush()

        for item in items:
            product = item["product"]
            product.stock -= item["cantidad"]
            order.detalles.append(
                OrderDetail(
                    id_producto=product.id_producto,
                    cantidad=item["cantidad"],
                    precio_venta=item["precio_venta"],
                )
            )
