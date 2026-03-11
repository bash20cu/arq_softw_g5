from flask import Blueprint

from app.controllers.frontend_order_controller import (
    crear_orden,
    detalle_orden,
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
