from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app.controllers.order_controller import OrderController
from app.controllers.product_controller import ProductController
from app.database import db
from app.models.user import Cliente
from app.views.order_view import OrderView


def _ensure_session():
    if session.get("user") is None:
        flash("Debes iniciar sesión para acceder a este módulo.", "error")
        return False
    return True


def _can_manage_orders():
    user = session.get("user")
    return user is not None and user.get("id_rol") in {1, 2}


def listar_ordenes():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _can_manage_orders():
        flash("No tienes permisos para consultar órdenes.", "error")
        return redirect(url_for("main.principal_page"))

    ordenes = OrderController.list_orders()
    return OrderView.render_lista(ordenes=ordenes, error=None)


def detalle_orden(orden_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _can_manage_orders():
        flash("No tienes permisos para consultar órdenes.", "error")
        return redirect(url_for("main.principal_page"))

    orden = OrderController.get_order_by_id(orden_id)
    if orden is None:
        flash("Orden no encontrada.", "error")
        return redirect(url_for("frontend_order.ordenes_listar"))
    return OrderView.render_detalle(orden, OrderController.calculate_total(orden))


def crear_orden():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _can_manage_orders():
        flash("No tienes permisos para generar órdenes.", "error")
        return redirect(url_for("main.principal_page"))

    clientes = Cliente.query.order_by(Cliente.id_cliente.asc()).all()
    productos = ProductController.list_products()

    if request.method == "POST":
        payload, form_errors = _parse_order_form()
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return OrderView.render_form(clientes, productos, payload)

        try:
            orden = OrderController.create_order(
                id_cliente=payload["id_cliente"],
                id_usuario=session["user"]["id_usuario"],
                detalles=payload["detalles"],
                estado="Pendiente",
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return OrderView.render_form(clientes, productos, payload)
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al generar la orden: {exc.orig}", "error")
            return OrderView.render_form(clientes, productos, payload)

        flash("Orden creada exitosamente.", "success")
        return redirect(url_for("frontend_order.ordenes_detalle", orden_id=orden.id_orden))

    return OrderView.render_form(clientes, productos, {})


def _parse_order_form():
    cliente = request.form.get("id_cliente", "").strip()
    product_ids = request.form.getlist("id_producto")
    cantidades = request.form.getlist("cantidad")

    errors = []
    detalles = []

    if not cliente:
        errors.append("Debe seleccionar un cliente.")
    elif not cliente.isdigit():
        errors.append("El cliente debe ser numérico.")

    for index, product_id in enumerate(product_ids):
        product_id = product_id.strip()
        cantidad = cantidades[index].strip() if index < len(cantidades) else ""

        if not product_id and not cantidad:
            continue
        if not product_id or not product_id.isdigit():
            errors.append("Cada línea debe tener un producto válido.")
            continue
        if not cantidad or not cantidad.isdigit():
            errors.append("Cada línea debe tener una cantidad numérica.")
            continue

        detalles.append(
            {"id_producto": int(product_id), "cantidad": int(cantidad)}
        )

    if not detalles:
        errors.append("Debe agregar al menos un producto a la orden.")

    return {
        "id_cliente": int(cliente) if cliente.isdigit() else cliente,
        "detalles": detalles,
    }, errors
