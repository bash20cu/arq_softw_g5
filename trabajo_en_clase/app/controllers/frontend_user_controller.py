from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app.controllers.persona_controller import PersonaController
from app.controllers.user_controller import UserController
from app.database import db
from app.views.user_view import UserView


def _ensure_session():
    if session.get("user") is None:
        flash("Debes iniciar sesión para acceder a este módulo.", "error")
        return False
    return True


def listar_usuarios():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    usuarios = UserController.list_users()
    return UserView.render_lista(usuarios=usuarios, error=None)


def detalle_usuario(usuario_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    usuario = UserController.get_user_by_id(usuario_id)
    if usuario is None:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("frontend.usuarios_listar"))
    return UserView.render_detalle(usuario=usuario)


def crear_usuario():
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    personas = UserController.list_personas_for_user()
    roles = PersonaController.list_roles()
    if request.method == "POST":
        data, form_errors = _parse_form(is_create=True)
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return UserView.render_form(
                usuario=data,
                action="crear",
                title="Nuevo Usuario",
                personas=personas,
                roles=roles,
            )

        try:
            UserController.create_user(**data)
        except ValueError as exc:
            flash(str(exc), "error")
            return UserView.render_form(
                usuario=data,
                action="crear",
                title="Nuevo Usuario",
                personas=personas,
                roles=roles,
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al crear usuario: {exc.orig}", "error")
            return UserView.render_form(
                usuario=data,
                action="crear",
                title="Nuevo Usuario",
                personas=personas,
                roles=roles,
            )

        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for("frontend.usuarios_listar"))

    return UserView.render_form(
        usuario={},
        action="crear",
        title="Nuevo Usuario",
        personas=personas,
        roles=roles,
    )


def editar_usuario(usuario_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    usuario = UserController.get_user_by_id(usuario_id)
    if usuario is None:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("frontend.usuarios_listar"))

    personas = UserController.list_personas_for_user(usuario.cedula_persona)
    roles = PersonaController.list_roles()

    if request.method == "POST":
        data, form_errors = _parse_form(is_create=False)
        if form_errors:
            for msg in form_errors:
                flash(msg, "error")
            return UserView.render_form(
                usuario=data,
                action="editar",
                title="Editar Usuario",
                personas=personas,
                roles=roles,
                usuario_id=usuario_id,
            )

        try:
            UserController.update_user(usuario, **data)
        except ValueError as exc:
            flash(str(exc), "error")
            return UserView.render_form(
                usuario=data,
                action="editar",
                title="Editar Usuario",
                personas=personas,
                roles=roles,
                usuario_id=usuario_id,
            )
        except IntegrityError as exc:
            db.session.rollback()
            flash(f"Error al actualizar usuario: {exc.orig}", "error")
            return UserView.render_form(
                usuario=data,
                action="editar",
                title="Editar Usuario",
                personas=personas,
                roles=roles,
                usuario_id=usuario_id,
            )

        flash("Usuario actualizado exitosamente.", "success")
        return redirect(url_for("frontend.usuarios_listar"))

    return UserView.render_form(
        usuario=usuario,
        action="editar",
        title="Editar Usuario",
        personas=personas,
        roles=roles,
        usuario_id=usuario_id,
    )


def eliminar_usuario(usuario_id):
    if not _ensure_session():
        return redirect(url_for("main.login_page"))
    usuario = UserController.get_user_by_id(usuario_id)
    if usuario is None:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("frontend.usuarios_listar"))

    try:
        UserController.delete_user(usuario)
    except IntegrityError as exc:
        db.session.rollback()
        flash(f"Error al eliminar usuario: {exc.orig}", "error")
    else:
        flash("Usuario eliminado exitosamente.", "success")
    return redirect(url_for("frontend.usuarios_listar"))


def _parse_form(*, is_create: bool):
    cedula = request.form.get("cedula_persona", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    id_rol = request.form.get("id_rol", "").strip()
    activo = request.form.get("activo") == "on"

    errors = []
    if not cedula:
        errors.append("La cédula es requerida.")
    if not username:
        errors.append("El nombre de usuario es requerido.")
    if is_create and not password:
        errors.append("La contraseña es requerida.")
    if not id_rol:
        errors.append("Debe seleccionar un rol.")
    elif not id_rol.isdigit():
        errors.append("El rol debe ser numérico.")

    data = {
        "cedula_persona": cedula,
        "username": username,
        "id_rol": int(id_rol) if id_rol.isdigit() else None,
        "activo": activo,
    }
    if password:
        data["password_hash"] = password

    return data, errors
