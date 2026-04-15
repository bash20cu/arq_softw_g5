from flask import Blueprint

from app.controllers.frontend_persona_controller import (
    crear_persona,
    detalle_persona,
    editar_persona,
    eliminar_persona,
    listar_personas,
)

frontend_persona_bp = Blueprint(
    "frontend_persona",
    __name__,
    url_prefix="/personas",
    template_folder="../views/templates",
)

frontend_persona_bp.add_url_rule("/", "personas_listar", listar_personas, methods=["GET"])
frontend_persona_bp.add_url_rule("/nuevo", "personas_crear", crear_persona, methods=["GET", "POST"])
frontend_persona_bp.add_url_rule("/<string:cedula>", "personas_detalle", detalle_persona, methods=["GET"])
frontend_persona_bp.add_url_rule(
    "/<string:cedula>/editar",
    "personas_editar",
    editar_persona,
    methods=["GET", "POST"],
)
frontend_persona_bp.add_url_rule(
    "/<string:cedula>/eliminar",
    "personas_eliminar",
    eliminar_persona,
    methods=["POST"],
)
