from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app.controllers.campaign_controller import CampaignController
from app.database import db
from app.views.campaign_view import CampaignView


def _ensure_session():
    if session.get("user") is None:
        flash("Debes iniciar sesión para acceder a este módulo.", "error")
        return False
    return True


def _require_admin():
    user = session.get("user")
    return user is not None and user.get("id_rol") == 1


def listar_campanias():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    campanias = CampaignController.list_campaigns()
    return CampaignView.render_lista(campanias, error=None)


def detalle_campania(campania_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    campania = CampaignController.get_campaign_by_id(campania_id)
    if campania is None:
        flash("Campaña no encontrada.", "error")
        return redirect(url_for("frontend_campaign.campanias_listar"))
    return CampaignView.render_detalle(campania)


def crear_campania():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _require_admin():
        flash("No tienes permisos para registrar campañas.", "error")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    if request.method == "POST":
        data, errors = _parse_form()
        if errors:
            for msg in errors:
                flash(msg, "error")
            return CampaignView.render_form(data, "crear", "Nueva Campaña")

        try:
            CampaignController.create_campaign(**data)
        except ValueError as exc:
            flash(str(exc), "error")
            return CampaignView.render_form(data, "crear", "Nueva Campaña")
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al crear campaña: {exc.orig}", "error")
            return CampaignView.render_form(data, "crear", "Nueva Campaña")

        flash("Campaña creada exitosamente.", "success")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    return CampaignView.render_form({}, "crear", "Nueva Campaña")


def editar_campania(campania_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _require_admin():
        flash("No tienes permisos para editar campañas.", "error")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    campania = CampaignController.get_campaign_by_id(campania_id)
    if campania is None:
        flash("Campaña no encontrada.", "error")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    if request.method == "POST":
        data, errors = _parse_form()
        if errors:
            for msg in errors:
                flash(msg, "error")
            return CampaignView.render_form(data, "editar", "Editar Campaña", campania_id)

        try:
            CampaignController.update_campaign(campania, **data)
        except ValueError as exc:
            flash(str(exc), "error")
            return CampaignView.render_form(data, "editar", "Editar Campaña", campania_id)
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al actualizar campaña: {exc.orig}", "error")
            return CampaignView.render_form(data, "editar", "Editar Campaña", campania_id)

        flash("Campaña actualizada exitosamente.", "success")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    return CampaignView.render_form(campania, "editar", "Editar Campaña", campania_id)


def eliminar_campania(campania_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    if not _require_admin():
        flash("No tienes permisos para eliminar campañas.", "error")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    campania = CampaignController.get_campaign_by_id(campania_id)
    if campania is None:
        flash("Campaña no encontrada.", "error")
        return redirect(url_for("frontend_campaign.campanias_listar"))

    try:
        CampaignController.delete_campaign(campania)
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al eliminar campaña: {exc.orig}", "error")
    else:
        flash("Campaña eliminada exitosamente.", "success")
    return redirect(url_for("frontend_campaign.campanias_listar"))


def _parse_form():
    nombre = request.form.get("nombre", "").strip()
    fecha_inicio = request.form.get("fecha_inicio", "").strip()
    fecha_fin = request.form.get("fecha_fin", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    errors = []
    if not nombre:
        errors.append("El nombre es requerido.")

    return {
        "nombre": nombre,
        "fecha_inicio": fecha_inicio or None,
        "fecha_fin": fecha_fin or None,
        "descripcion": descripcion or None,
    }, errors
