from flask import Blueprint

from app.controllers.frontend_campaign_controller import (
    crear_campania,
    detalle_campania,
    editar_campania,
    eliminar_campania,
    listar_campanias,
)

frontend_campaign_bp = Blueprint(
    "frontend_campaign",
    __name__,
    url_prefix="/campanias",
    template_folder="../views/templates",
)

frontend_campaign_bp.add_url_rule("/", "campanias_listar", listar_campanias, methods=["GET"])
frontend_campaign_bp.add_url_rule("/nuevo", "campanias_crear", crear_campania, methods=["GET", "POST"])
frontend_campaign_bp.add_url_rule("/<int:campania_id>", "campanias_detalle", detalle_campania, methods=["GET"])
frontend_campaign_bp.add_url_rule(
    "/<int:campania_id>/editar", "campanias_editar", editar_campania, methods=["GET", "POST"]
)
frontend_campaign_bp.add_url_rule(
    "/<int:campania_id>/eliminar", "campanias_eliminar", eliminar_campania, methods=["POST"]
)
