from decimal import Decimal, InvalidOperation

from sqlalchemy import func

from app.controllers.campaign_controller import CampaignController
from app.database import db
from app.models.product import Product


class ProductController:
    @staticmethod
    def list_products() -> list[Product]:
        return Product.query.order_by(Product.id_producto.asc()).all()

    @staticmethod
    def get_product_by_id(product_id: int) -> Product | None:
        return Product.query.filter_by(id_producto=product_id).first()

    @staticmethod
    def create_product(
        nombre: str,
        precio_actual,
        stock,
        id_campania: int | None = None,
    ) -> Product:
        normalized_name = ProductController._validate_name(nombre)
        ProductController._validate_unique_name(normalized_name)
        product = Product(
            nombre=normalized_name,
            precio_actual=ProductController._validate_price(precio_actual),
            stock=ProductController._validate_stock(stock),
            id_campania=ProductController._validate_campaign(id_campania),
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(product: Product, **fields) -> Product:
        if "nombre" in fields:
            normalized_name = ProductController._validate_name(fields["nombre"])
            ProductController._validate_unique_name(
                normalized_name, current_product_id=product.id_producto
            )
            product.nombre = normalized_name
        if "precio_actual" in fields:
            product.precio_actual = ProductController._validate_price(fields["precio_actual"])
        if "stock" in fields:
            product.stock = ProductController._validate_stock(fields["stock"])
        if "id_campania" in fields:
            product.id_campania = ProductController._validate_campaign(fields["id_campania"])

        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def delete_product(product: Product) -> None:
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def _validate_name(value: str) -> str:
        name = (value or "").strip()
        if not name:
            raise ValueError("nombre es obligatorio")
        return name

    @staticmethod
    def _validate_unique_name(value: str, current_product_id: int | None = None) -> None:
        query = Product.query.filter(func.lower(Product.nombre) == value.lower())
        if current_product_id is not None:
            query = query.filter(Product.id_producto != current_product_id)
        if query.first() is not None:
            raise ValueError("ya existe un producto con ese nombre")

    @staticmethod
    def _validate_price(value) -> Decimal:
        try:
            price = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("precio_actual debe ser numerico") from exc
        if price <= 0:
            raise ValueError("precio_actual debe ser mayor a cero")
        return price.quantize(Decimal("0.01"))

    @staticmethod
    def _validate_stock(value) -> int:
        try:
            stock = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("stock debe ser numerico") from exc
        if stock < 0:
            raise ValueError("stock no puede ser negativo")
        return stock

    @staticmethod
    def list_campaigns():
        return CampaignController.list_campaigns()

    @staticmethod
    def _validate_campaign(value) -> int | None:
        if value in (None, "", 0, "0"):
            return None
        try:
            campaign_id = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("id_campania debe ser numerico") from exc
        if CampaignController.get_campaign_by_id(campaign_id) is None:
            raise ValueError("id_campania no existe")
        return campaign_id
