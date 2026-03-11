from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app.controllers.product_controller import ProductController
from app.database import db
from app.views.product_view import ProductView


def _ensure_session():
    if session.get("user") is None:
        flash("Debes iniciar sesión para acceder a este módulo.", "error")
        return False
    return True


def _require_admin():
    user = session.get("user")
    return user is not None and user.get("id_rol") == 1


def listar_productos():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    productos = ProductController.list_products()
    return ProductView.render_lista(productos=productos, error=None)


def detalle_producto(producto_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    producto = ProductController.get_product_by_id(producto_id)
    if producto is None:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("frontend_product.productos_listar"))
    return ProductView.render_detalle(producto)


def crear_producto():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _require_admin():
        flash("No tienes permisos para registrar productos.", "error")
        return redirect(url_for("frontend_product.productos_listar"))

    if request.method == "POST":
        data, form_errors = _parse_form()
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return ProductView.render_form(
                producto=data,
                action="crear",
                title="Nuevo Producto",
            )

        try:
            ProductController.create_product(**data)
        except ValueError as exc:
            flash(str(exc), "error")
            return ProductView.render_form(
                producto=data,
                action="crear",
                title="Nuevo Producto",
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al crear producto: {exc.orig}", "error")
            return ProductView.render_form(
                producto=data,
                action="crear",
                title="Nuevo Producto",
            )

        flash("Producto creado exitosamente.", "success")
        return redirect(url_for("frontend_product.productos_listar"))

    return ProductView.render_form(producto={}, action="crear", title="Nuevo Producto")


def editar_producto(producto_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _require_admin():
        flash("No tienes permisos para editar productos.", "error")
        return redirect(url_for("frontend_product.productos_listar"))

    producto = ProductController.get_product_by_id(producto_id)
    if producto is None:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("frontend_product.productos_listar"))

    if request.method == "POST":
        data, form_errors = _parse_form()
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return ProductView.render_form(
                producto=data,
                action="editar",
                title="Editar Producto",
                producto_id=producto_id,
            )

        try:
            ProductController.update_product(producto, **data)
        except ValueError as exc:
            flash(str(exc), "error")
            return ProductView.render_form(
                producto=data,
                action="editar",
                title="Editar Producto",
                producto_id=producto_id,
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al actualizar producto: {exc.orig}", "error")
            return ProductView.render_form(
                producto=data,
                action="editar",
                title="Editar Producto",
                producto_id=producto_id,
            )

        flash("Producto actualizado exitosamente.", "success")
        return redirect(url_for("frontend_product.productos_listar"))

    return ProductView.render_form(
        producto=producto,
        action="editar",
        title="Editar Producto",
        producto_id=producto_id,
    )


def eliminar_producto(producto_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _require_admin():
        flash("No tienes permisos para eliminar productos.", "error")
        return redirect(url_for("frontend_product.productos_listar"))

    producto = ProductController.get_product_by_id(producto_id)
    if producto is None:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("frontend_product.productos_listar"))

    try:
        ProductController.delete_product(producto)
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al eliminar producto: {exc.orig}", "error")
    else:
        flash("Producto eliminado exitosamente.", "success")
    return redirect(url_for("frontend_product.productos_listar"))


def _parse_form():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio_actual", "").strip()
    stock = request.form.get("stock", "").strip()
    campania = request.form.get("id_campania", "").strip()

    errors = []
    if not nombre:
        errors.append("El nombre es requerido.")
    if not precio:
        errors.append("El precio es requerido.")
    if not stock:
        errors.append("El stock es requerido.")
    if campania and not campania.isdigit():
        errors.append("La campaña debe ser numérica.")

    return {
        "nombre": nombre,
        "precio_actual": precio,
        "stock": stock,
        "id_campania": int(campania) if campania.isdigit() else None,
    }, errors
