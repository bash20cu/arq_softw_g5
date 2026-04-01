from functools import wraps

from flask import session

from app.controllers.client_controller import ClientController
from app.views.user_view import error_response


# Role ids are kept in one place so every route module enforces the same policy.
ROLE_ADMIN = 1
ROLE_EMPLEADO = 2
ROLE_CLIENTE = 3


def login_required(fn):
    """Require an authenticated session before entering the route handler."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("user") is None:
            return error_response("sesion no verificada", 401)
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*allowed_roles):
    """Require that the current session user belongs to one of the allowed roles."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if user is None:
                return error_response("sesion no verificada", 401)
            if user.get("id_rol") not in allowed_roles:
                return error_response("forbidden", 403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def current_session_user() -> dict:
    """Return the current session identity or raise if the session is missing."""

    user = session.get("user")
    if user is None:
        raise PermissionError("sesion no verificada")
    return user


def is_staff(user: dict) -> bool:
    """Staff users keep broad operational access to backoffice resources."""

    return user.get("id_rol") in {ROLE_ADMIN, ROLE_EMPLEADO}


def get_current_client():
    """Resolve the customer record tied to the logged-in client session."""

    user = current_session_user()
    if user.get("id_rol") != ROLE_CLIENTE:
        return None
    client = ClientController.get_client_by_cedula(user.get("cedula_persona") or "")
    if client is None:
        raise PermissionError("forbidden")
    return client


def ensure_client_access(cliente) -> None:
    """Allow staff to inspect any client and customers only their own record."""

    user = current_session_user()
    if is_staff(user):
        return

    current_client = get_current_client()
    if current_client is None or current_client.id_cliente != cliente.id_cliente:
        raise PermissionError("forbidden")


def ensure_order_access(order) -> None:
    """Allow staff to inspect any order and customers only their own orders."""

    user = current_session_user()
    if is_staff(user):
        return

    current_client = get_current_client()
    if current_client is None or current_client.id_cliente != order.id_cliente:
        raise PermissionError("forbidden")
