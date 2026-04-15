from flask import Blueprint

from app.controllers.frontend_product_controller import (
    crear_producto,
    detalle_producto,
    editar_producto,
    eliminar_producto,
    listar_productos,
)

frontend_product_bp = Blueprint(
    "frontend_product",
    __name__,
    url_prefix="/productos",
    template_folder="../views/templates",
)

frontend_product_bp.add_url_rule("/", "productos_listar", listar_productos, methods=["GET"])
frontend_product_bp.add_url_rule(
    "/nuevo", "productos_crear", crear_producto, methods=["GET", "POST"]
)
frontend_product_bp.add_url_rule(
    "/<int:producto_id>", "productos_detalle", detalle_producto, methods=["GET"]
)
frontend_product_bp.add_url_rule(
    "/<int:producto_id>/editar",
    "productos_editar",
    editar_producto,
    methods=["GET", "POST"],
)
frontend_product_bp.add_url_rule(
    "/<int:producto_id>/eliminar",
    "productos_eliminar",
    eliminar_producto,
    methods=["POST"],
)
