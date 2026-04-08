"""Funciones auxiliares compartidas entre distintos modulos de rutas."""

from app.controllers.order_controller import OrderController


def to_bool(value):
    """Normaliza valores truthy/falsy recibidos desde formularios o JSON."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "si", "yes"}
    return bool(value)


def filter_allowed_fields(payload: dict, allowed_fields: set[str]) -> dict:
    """Filtra el payload y conserva solo los campos editables permitidos."""

    return {key: value for key, value in payload.items() if key in allowed_fields}


def serialize_order(order, *, include_details: bool) -> dict:
    """Serializa una orden agregando total y transiciones disponibles."""

    payload = order.to_dict(include_details=include_details)
    payload["total"] = OrderController.calculate_total(order)
    payload["available_transitions"] = OrderController.get_available_transitions(order)
    return payload


def serialize_order_status(order) -> dict:
    """Expone la vista compacta del estado usada por el seguimiento de pedidos."""

    payload = serialize_order(order, include_details=False)
    return {
        "id_orden": payload["id_orden"],
        "estado": payload["estado"],
        "fecha_orden": payload["fecha_orden"],
        "total": payload["total"],
    }
