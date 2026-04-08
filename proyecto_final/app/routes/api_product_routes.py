"""Rutas CRUD de productos."""

from flask import request
from sqlalchemy.exc import IntegrityError

from app.controllers.product_controller import ProductController
from app.database import db
from app.routes.api_authz import ROLE_ADMIN, ROLE_EMPLEADO, roles_required
from app.routes.api_helpers import filter_allowed_fields, to_bool
from app.views.user_view import error_response


def register_product_routes(bp):
    """Product routes handle CRUD concerns while delegating rules to the controller."""

    @bp.get("/productos")
    def list_products():
        """Lista los productos visibles del catalogo."""

        products = ProductController.list_products()
        return [product.to_dict() for product in products], 200

    @bp.get("/productos/<int:product_id>")
    def get_product(product_id: int):
        """Obtiene un producto especifico por id."""

        product = ProductController.get_product_by_id(product_id)
        if product is None:
            return error_response("producto no encontrado", 404)
        return product.to_dict(), 200

    @bp.post("/productos")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def create_product():
        """Crea un producto nuevo usando el payload recibido por JSON."""

        payload = request.get_json(silent=True) or {}
        try:
            product = ProductController.create_product(
                nombre=payload.get("nombre"),
                descripcion=payload.get("descripcion"),
                fotografia_url=payload.get("fotografia_url"),
                color_estilo=payload.get("color_estilo"),
                codigo_barras=payload.get("codigo_barras"),
                precio_base=payload.get("precio_base"),
                iva_porcentaje=payload.get("iva_porcentaje", 13),
                stock=payload.get("stock"),
                activo=to_bool(payload.get("activo", True)),
            )
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("no fue posible registrar el producto", 409)

        return product.to_dict(), 201

    @bp.put("/productos/<int:product_id>")
    @roles_required(ROLE_ADMIN, ROLE_EMPLEADO)
    def update_product(product_id: int):
        """Actualiza un producto existente."""

        product = ProductController.get_product_by_id(product_id)
        if product is None:
            return error_response("producto no encontrado", 404)

        payload = request.get_json(silent=True) or {}
        allowed_fields = {
            "nombre",
            "descripcion",
            "fotografia_url",
            "color_estilo",
            "codigo_barras",
            "precio_base",
            "iva_porcentaje",
            "stock",
            "activo",
        }
        update_fields = filter_allowed_fields(payload, allowed_fields)
        if "activo" in update_fields:
            update_fields["activo"] = to_bool(update_fields["activo"])
        if not update_fields:
            return error_response("no hay campos validos para actualizar", 400)

        try:
            updated = ProductController.update_product(product, **update_fields)
        except ValueError as exc:
            db.session.rollback()
            return error_response(str(exc), 400)
        except IntegrityError:
            db.session.rollback()
            return error_response("no fue posible actualizar el producto", 409)

        return updated.to_dict(), 200

    @bp.delete("/productos/<int:product_id>")
    @roles_required(ROLE_ADMIN)
    def delete_product(product_id: int):
        """Elimina un producto del catalogo."""

        product = ProductController.get_product_by_id(product_id)
        if product is None:
            return error_response("producto no encontrado", 404)
        try:
            ProductController.delete_product(product)
        except IntegrityError:
            db.session.rollback()
            return error_response("producto en uso por otras tablas", 409)
        return {"ok": True, "message": "producto eliminado"}, 200
