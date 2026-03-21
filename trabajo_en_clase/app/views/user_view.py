from flask import jsonify
from flask import render_template


def users_response(items: list[dict]):
    return jsonify(items), 200


def created_user_response(item: dict):
    return jsonify(item), 201


def error_response(message: str, status: int):
    return jsonify({"error": message}), status


class UserView:
    @staticmethod
    def render_lista(usuarios, error):
        return render_template(
            'usuarios/lista.html',
            usuarios=usuarios,
            error=error
        )

    @staticmethod
    def render_detalle(usuario):
        return render_template(
            'usuarios/detalle.html',
            usuario=usuario
        )

    @staticmethod
    def render_form(usuario, action, title, personas, roles, usuario_id=None):
        return render_template(
            'usuarios/form.html',
            usuario=usuario,
            action=action,
            title=title,
            usuario_id=usuario_id,
            personas=personas,
            roles=roles,
        )
