from flask import Blueprint

from app.controllers.frontend_client_controller import (
    crear_cliente,
    detalle_cliente,
    editar_cliente,
    eliminar_cliente,
    listar_clientes,
)

frontend_client_bp = Blueprint(
    "frontend_client",
    __name__,
    url_prefix="/clientes",
    template_folder="../views/templates",
)

frontend_client_bp.add_url_rule("/", "clientes_listar", listar_clientes, methods=["GET"])
frontend_client_bp.add_url_rule("/nuevo", "clientes_crear", crear_cliente, methods=["GET", "POST"])
frontend_client_bp.add_url_rule(
    "/<int:cliente_id>", "clientes_detalle", detalle_cliente, methods=["GET"]
)
frontend_client_bp.add_url_rule(
    "/<int:cliente_id>/editar",
    "clientes_editar",
    editar_cliente,
    methods=["GET", "POST"],
)
frontend_client_bp.add_url_rule(
    "/<int:cliente_id>/eliminar",
    "clientes_eliminar",
    eliminar_cliente,
    methods=["POST"],
)
