from flask import Blueprint

from app.controllers.frontend_order_controller import (
    cancelar_orden,
    cambiar_estado_orden,
    crear_orden,
    detalle_orden,
    editar_orden,
    listar_ordenes,
)

frontend_order_bp = Blueprint(
    "frontend_order",
    __name__,
    url_prefix="/ordenes",
    template_folder="../views/templates",
)

frontend_order_bp.add_url_rule("/", "ordenes_listar", listar_ordenes, methods=["GET"])
frontend_order_bp.add_url_rule("/nuevo", "ordenes_crear", crear_orden, methods=["GET", "POST"])
frontend_order_bp.add_url_rule(
    "/<int:orden_id>", "ordenes_detalle", detalle_orden, methods=["GET"]
)
frontend_order_bp.add_url_rule(
    "/<int:orden_id>/editar",
    "ordenes_editar",
    editar_orden,
    methods=["GET", "POST"],
)
frontend_order_bp.add_url_rule(
    "/<int:orden_id>/cancelar",
    "ordenes_cancelar",
    cancelar_orden,
    methods=["POST"],
)
frontend_order_bp.add_url_rule(
    "/<int:orden_id>/estado",
    "ordenes_cambiar_estado",
    cambiar_estado_orden,
    methods=["POST"],
)
