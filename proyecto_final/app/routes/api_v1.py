"""Composition root del API REST version 1.

Este archivo no contiene logica de negocio; solo crea el blueprint principal
y registra los modulos de rutas especializados por contexto.
"""

from flask import Blueprint

from app.routes.api_auth_routes import register_auth_routes
from app.routes.api_catalog_routes import register_catalog_routes
from app.routes.api_client_routes import register_client_routes
from app.routes.api_order_routes import register_order_routes
from app.routes.api_payment_routes import register_payment_routes
from app.routes.api_persona_routes import register_persona_routes
from app.routes.api_product_routes import register_product_routes
from app.routes.api_user_routes import register_user_routes


# This module is now the composition root of the REST API. Each bounded context
# registers its own routes in a dedicated module so the design stays modular and
# respects single-responsibility boundaries.
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


register_catalog_routes(api_v1_bp)
register_persona_routes(api_v1_bp)
register_product_routes(api_v1_bp)
register_client_routes(api_v1_bp)
register_user_routes(api_v1_bp)
register_auth_routes(api_v1_bp)
register_order_routes(api_v1_bp)
register_payment_routes(api_v1_bp)
