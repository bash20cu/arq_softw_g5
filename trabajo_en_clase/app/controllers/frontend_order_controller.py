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
    return OrderView.render_detalle(
        orden,
        OrderController.calculate_total(orden),
        OrderController.get_available_transitions(orden),
    )


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


def editar_orden(orden_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _can_manage_orders():
        flash("No tienes permisos para editar órdenes.", "error")
        return redirect(url_for("main.principal_page"))

    orden = OrderController.get_order_by_id(orden_id)
    if orden is None:
        flash("Orden no encontrada.", "error")
        return redirect(url_for("frontend_order.ordenes_listar"))
    if orden.estado == "Cancelado":
        flash("No se puede editar una orden cancelada.", "error")
        return redirect(url_for("frontend_order.ordenes_detalle", orden_id=orden_id))

    clientes = Cliente.query.order_by(Cliente.id_cliente.asc()).all()
    productos = ProductController.list_products()

    if request.method == "POST":
        payload, form_errors = _parse_order_form()
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return OrderView.render_form(clientes, productos, payload, order=orden, is_edit=True)

        try:
            orden = OrderController.update_order(
                orden,
                id_cliente=payload["id_cliente"],
                detalles=payload["detalles"],
                estado=payload.get("estado"),
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return OrderView.render_form(clientes, productos, payload, order=orden, is_edit=True)
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al actualizar la orden: {exc.orig}", "error")
            return OrderView.render_form(clientes, productos, payload, order=orden, is_edit=True)

        flash("Orden actualizada exitosamente.", "success")
        return redirect(url_for("frontend_order.ordenes_detalle", orden_id=orden.id_orden))

    return OrderView.render_form(
        clientes,
        productos,
        {
            "id_cliente": orden.id_cliente,
            "estado": orden.estado,
            "detalles": [
                {"id_producto": detalle.id_producto, "cantidad": detalle.cantidad}
                for detalle in orden.detalles
            ],
        },
        order=orden,
        is_edit=True,
    )


def cancelar_orden(orden_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _can_manage_orders():
        flash("No tienes permisos para cancelar órdenes.", "error")
        return redirect(url_for("main.principal_page"))

    orden = OrderController.get_order_by_id(orden_id)
    if orden is None:
        flash("Orden no encontrada.", "error")
        return redirect(url_for("frontend_order.ordenes_listar"))

    try:
        OrderController.cancel_order(orden)
    except ValueError as exc:
        flash(str(exc), "error")
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al cancelar la orden: {exc.orig}", "error")
    else:
        flash("Orden cancelada exitosamente.", "success")

    return redirect(url_for("frontend_order.ordenes_detalle", orden_id=orden_id))


def cambiar_estado_orden(orden_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _can_manage_orders():
        flash("No tienes permisos para actualizar órdenes.", "error")
        return redirect(url_for("main.principal_page"))

    orden = OrderController.get_order_by_id(orden_id)
    if orden is None:
        flash("Orden no encontrada.", "error")
        return redirect(url_for("frontend_order.ordenes_listar"))

    nuevo_estado = request.form.get("estado", "").strip()
    try:
        OrderController.transition_order(orden, nuevo_estado)
    except ValueError as exc:
        flash(str(exc), "error")
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al cambiar estado: {exc.orig}", "error")
    else:
        flash(f"Orden actualizada a estado {nuevo_estado}.", "success")

    return redirect(
        request.form.get("next")
        or url_for("frontend_order.ordenes_detalle", orden_id=orden_id)
    )


def _parse_order_form():
    cliente = request.form.get("id_cliente", "").strip()
    estado = request.form.get("estado", "").strip()
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
        "estado": estado or None,
        "detalles": detalles,
    }, errors
