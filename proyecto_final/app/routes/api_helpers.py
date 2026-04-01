from app.controllers.order_controller import OrderController


def to_bool(value):
    """Normalize HTML/JSON truthy values used by the forms and API payloads."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "si", "yes"}
    return bool(value)


def filter_allowed_fields(payload: dict, allowed_fields: set[str]) -> dict:
    """Keep only the mutable fields accepted by a route handler."""

    return {key: value for key, value in payload.items() if key in allowed_fields}


def serialize_order(order, *, include_details: bool) -> dict:
    """Build a standard order payload with the calculated total included."""

    payload = order.to_dict(include_details=include_details)
    payload["total"] = OrderController.calculate_total(order)
    payload["available_transitions"] = OrderController.get_available_transitions(order)
    return payload


def serialize_order_status(order) -> dict:
    """Expose the compact status view used by the order tracking screen."""

    payload = serialize_order(order, include_details=False)
    return {
        "id_orden": payload["id_orden"],
        "estado": payload["estado"],
        "fecha_orden": payload["fecha_orden"],
        "total": payload["total"],
    }
