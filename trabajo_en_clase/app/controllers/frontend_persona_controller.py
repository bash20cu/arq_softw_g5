from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app.controllers.persona_controller import PersonaController
from app.database import db
from app.views.persona_view import PersonaView


def _ensure_session():
    if session.get("user") is None:
        flash("Debes iniciar sesión para acceder a este módulo.", "error")
        return False
    return True


def listar_personas():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    personas = PersonaController.list_personas()
    return PersonaView.render_lista(personas, error=None)


def detalle_persona(cedula):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    persona = PersonaController.get_persona_by_cedula(cedula)
    if persona is None:
        flash("Persona no encontrada.", "error")
        return redirect(url_for("frontend_persona.personas_listar"))
    return PersonaView.render_detalle(persona)


def crear_persona():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))

    provincias = PersonaController.list_provincias()
    if request.method == "POST":
        data, form_errors = _parse_form(is_create=True)
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return PersonaView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "crear",
                "Nueva Persona",
            )

        try:
            PersonaController.create_persona(**data)
        except ValueError as exc:
            flash(str(exc), "error")
            return PersonaView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "crear",
                "Nueva Persona",
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al crear persona: {exc.orig}", "error")
            return PersonaView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "crear",
                "Nueva Persona",
            )

        flash("Persona creada exitosamente.", "success")
        return redirect(url_for("frontend_persona.personas_listar"))

    return PersonaView.render_form(
        {}, provincias, {"id_provincia": None, "id_canton": None, "id_distrito": None}, "crear", "Nueva Persona"
    )


def editar_persona(cedula):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))

    persona = PersonaController.get_persona_by_cedula(cedula)
    if persona is None:
        flash("Persona no encontrada.", "error")
        return redirect(url_for("frontend_persona.personas_listar"))

    provincias = PersonaController.list_provincias()
    if request.method == "POST":
        data, form_errors = _parse_form(is_create=False)
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            data["cedula"] = cedula
            return PersonaView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "editar",
                "Editar Persona",
                cedula,
            )

        try:
            PersonaController.update_persona(persona, **data)
        except ValueError as exc:
            flash(str(exc), "error")
            data["cedula"] = cedula
            return PersonaView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "editar",
                "Editar Persona",
                cedula,
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al actualizar persona: {exc.orig}", "error")
            data["cedula"] = cedula
            return PersonaView.render_form(
                data,
                provincias,
                PersonaController.get_location_selection(data.get("id_distrito")),
                "editar",
                "Editar Persona",
                cedula,
            )

        flash("Persona actualizada exitosamente.", "success")
        return redirect(url_for("frontend_persona.personas_listar"))

    return PersonaView.render_form(
        persona,
        provincias,
        PersonaController.get_location_selection(persona.id_distrito),
        "editar",
        "Editar Persona",
        cedula,
    )


def eliminar_persona(cedula):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))

    persona = PersonaController.get_persona_by_cedula(cedula)
    if persona is None:
        flash("Persona no encontrada.", "error")
        return redirect(url_for("frontend_persona.personas_listar"))

    try:
        PersonaController.delete_persona(persona)
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al eliminar persona: {exc.orig}", "error")
    else:
        flash("Persona eliminada exitosamente.", "success")
    return redirect(url_for("frontend_persona.personas_listar"))


def _parse_form(*, is_create: bool):
    cedula = request.form.get("cedula", "").strip()
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip()
    telefono = request.form.get("telefono", "").strip()
    id_distrito = request.form.get("id_distrito", "").strip()

    errors = []
    if is_create and not cedula:
        errors.append("La cédula es requerida.")
    if not nombre:
        errors.append("El nombre es requerido.")
    if not apellido:
        errors.append("El apellido es requerido.")
    if not email:
        errors.append("El email es requerido.")
    if id_distrito and not id_distrito.isdigit():
        errors.append("El distrito debe ser numérico.")

    payload = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "telefono": telefono or None,
        "id_distrito": int(id_distrito) if id_distrito.isdigit() else None,
    }
    if is_create:
        payload["cedula"] = cedula
    return payload, errors
