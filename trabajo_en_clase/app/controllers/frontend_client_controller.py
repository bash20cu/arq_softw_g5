from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app.controllers.client_controller import ClientController
from app.controllers.persona_controller import PersonaController
from app.database import db
from app.views.client_view import ClientView


def _ensure_session():
    if session.get("user") is None:
        flash("Debes iniciar sesión para acceder a este módulo.", "error")
        return False
    return True


def listar_clientes():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    clientes = ClientController.list_clients()
    return ClientView.render_lista(clientes, error=None)


def detalle_cliente(cliente_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    cliente = ClientController.get_client_by_id(cliente_id)
    if cliente is None:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("frontend_client.clientes_listar"))
    return ClientView.render_detalle(cliente)


def crear_cliente():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))

    provincias = PersonaController.list_provincias()
    if request.method == "POST":
        data, form_errors = _parse_form()
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return ClientView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "crear",
                "Nuevo Cliente",
            )

        try:
            ClientController.create_client(**data)
        except ValueError as exc:
            flash(str(exc), "error")
            return ClientView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "crear",
                "Nuevo Cliente",
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al crear cliente: {exc.orig}", "error")
            return ClientView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "crear",
                "Nuevo Cliente",
            )

        flash("Cliente creado exitosamente.", "success")
        return redirect(url_for("frontend_client.clientes_listar"))

    return ClientView.render_form(
        {},
        provincias,
        {"id_provincia": None, "id_canton": None, "id_distrito": None},
        "crear",
        "Nuevo Cliente",
    )


def editar_cliente(cliente_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))

    cliente = ClientController.get_client_by_id(cliente_id)
    if cliente is None:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("frontend_client.clientes_listar"))

    provincias = PersonaController.list_provincias()
    if request.method == "POST":
        data, form_errors = _parse_form()
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return ClientView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "editar",
                "Editar Cliente",
                cliente_id,
            )

        try:
            ClientController.update_client(cliente, **data)
        except ValueError as exc:
            flash(str(exc), "error")
            return ClientView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "editar",
                "Editar Cliente",
                cliente_id,
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al actualizar cliente: {exc.orig}", "error")
            return ClientView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "editar",
                "Editar Cliente",
                cliente_id,
            )

        flash("Cliente actualizado exitosamente.", "success")
        return redirect(url_for("frontend_client.clientes_listar"))

    return ClientView.render_form(
        cliente,
        provincias,
        PersonaController.get_location_selection(cliente.id_distrito),
        "editar",
        "Editar Cliente",
        cliente_id,
    )


def eliminar_cliente(cliente_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))

    cliente = ClientController.get_client_by_id(cliente_id)
    if cliente is None:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("frontend_client.clientes_listar"))

    try:
        ClientController.delete_client(cliente)
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al eliminar cliente: {exc.orig}", "error")
    else:
        flash("Cliente eliminado exitosamente.", "success")
    return redirect(url_for("frontend_client.clientes_listar"))


def _parse_form():
    cedula_persona = request.form.get("cedula_persona", "").strip()
    tipo_cliente = request.form.get("tipo_cliente", "").strip()
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip()
    telefono = request.form.get("telefono", "").strip()
    id_distrito = request.form.get("id_distrito", "").strip()
    puntos_lealtad = request.form.get("puntos_lealtad", "").strip()
    estado_cliente = request.form.get("estado_cliente", "").strip()

    errors = []
    if tipo_cliente not in {"Persona", "Empresa"}:
        errors.append("Debes seleccionar si el cliente es persona o empresa.")
    if not nombre:
        errors.append("El nombre es requerido.")
    if tipo_cliente != "Empresa" and not apellido:
        errors.append("El apellido es requerido.")
    if not email:
        errors.append("El email es requerido.")
    if id_distrito and not id_distrito.isdigit():
        errors.append("El distrito debe ser numérico.")
    if puntos_lealtad and not puntos_lealtad.isdigit():
        errors.append("Los puntos deben ser numéricos.")

    return {
        "cedula_persona": cedula_persona or None,
        "tipo_cliente": tipo_cliente or "Persona",
        "nombre": nombre,
        "apellido": apellido or None,
        "email": email,
        "telefono": telefono or None,
        "id_distrito": int(id_distrito) if id_distrito.isdigit() else None,
        "puntos_lealtad": int(puntos_lealtad) if puntos_lealtad.isdigit() else 0,
        "estado_cliente": estado_cliente or "Activo",
    }, errors
