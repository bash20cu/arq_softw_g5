"""Funciones auxiliares para respuestas JSON y vistas ligadas a usuarios."""

from flask import jsonify
from flask import render_template


def users_response(items: list[dict]):
    """Devuelve una lista JSON de usuarios con codigo 200."""

    return jsonify(items), 200


def created_user_response(item: dict):
    """Devuelve un recurso creado con codigo 201."""

    return jsonify(item), 201


def error_response(message: str, status: int):
    """Uniforma las respuestas de error del backend."""

    return jsonify({"error": message}), status


class UserView:
    """Renderiza plantillas HTML historicas relacionadas con usuarios."""

    @staticmethod
    def render_lista(usuarios, error):
        """Renderiza la lista HTML de usuarios."""

        return render_template(
            'usuarios/lista.html',
            usuarios=usuarios,
            error=error
        )

    @staticmethod
    def render_detalle(usuario):
        """Renderiza el detalle HTML de un usuario."""

        return render_template(
            'usuarios/detalle.html',
            usuario=usuario
        )

    @staticmethod
    def render_form(usuario, action, title, personas, roles, usuario_id=None):
        """Renderiza el formulario HTML de creacion o edicion de usuario."""

        return render_template(
            'usuarios/form.html',
            usuario=usuario,
            action=action,
            title=title,
            usuario_id=usuario_id,
            personas=personas,
            roles=roles,
        )
