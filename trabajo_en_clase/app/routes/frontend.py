from flask import Blueprint

from app.controllers.frontend_user_controller import (
    crear_usuario,
    detalle_usuario,
    editar_usuario,
    eliminar_usuario,
    listar_usuarios,
)

frontend_bp = Blueprint(
    "frontend",
    __name__,
    url_prefix="/usuarios",
    template_folder="../views/templates",
)

frontend_bp.add_url_rule("/", "usuarios_listar", listar_usuarios, methods=["GET"])
frontend_bp.add_url_rule(
    "/nuevo", "usuarios_crear", crear_usuario, methods=["GET", "POST"]
)
frontend_bp.add_url_rule(
    "/<int:usuario_id>", "usuarios_detalle", detalle_usuario, methods=["GET"]
)
frontend_bp.add_url_rule(
    "/<int:usuario_id>/editar",
    "usuarios_editar",
    editar_usuario,
    methods=["GET", "POST"],
)
frontend_bp.add_url_rule(
    "/<int:usuario_id>/eliminar",
    "usuarios_eliminar",
    eliminar_usuario,
    methods=["POST"],
)
