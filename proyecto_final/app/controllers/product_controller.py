"""Controlador de productos.

Centraliza las reglas de catalogo, precio, IVA y stock para el inventario.
"""

from decimal import Decimal, InvalidOperation

from app.database import db
from app.models.product import Product


class ProductController:
    @staticmethod
    def list_products() -> list[Product]:
        """Lista todos los productos registrados."""

        return Product.query.order_by(Product.id_producto.asc()).all()

    @staticmethod
    def get_product_by_id(product_id: int) -> Product | None:
        """Busca un producto por su identificador."""

        return Product.query.filter_by(id_producto=product_id).first()

    @staticmethod
    def create_product(
        nombre: str,
        precio_base,
        stock,
        descripcion: str | None = None,
        fotografia_url: str | None = None,
        color_estilo: str | None = None,
        codigo_barras: str | None = None,
        iva_porcentaje=13,
        activo: bool = True,
    ) -> Product:
        """Crea un producto calculando su precio final con IVA."""

        normalized_name = ProductController._validate_name(nombre)
        ProductController._validate_unique_name(normalized_name)
        normalized_base = ProductController._validate_price(precio_base, "precio_base")
        normalized_iva = ProductController._validate_price(iva_porcentaje, "iva_porcentaje")
        product = Product(
            nombre=normalized_name,
            descripcion=(descripcion or "").strip() or None,
            fotografia_url=(fotografia_url or "").strip() or None,
            color_estilo=(color_estilo or "").strip() or None,
            codigo_barras=(codigo_barras or "").strip() or None,
            precio_base=normalized_base,
            iva_porcentaje=normalized_iva,
            precio_actual=ProductController._calculate_final_price(normalized_base, normalized_iva),
            stock=ProductController._validate_stock(stock),
            activo=bool(activo),
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(product: Product, **fields) -> Product:
        """Actualiza un producto y recalcula el precio final cuando corresponde."""

        if "nombre" in fields:
            normalized_name = ProductController._validate_name(fields["nombre"])
            ProductController._validate_unique_name(
                normalized_name, current_product_id=product.id_producto
            )
            product.nombre = normalized_name
        if "descripcion" in fields:
            product.descripcion = (fields["descripcion"] or "").strip() or None
        if "fotografia_url" in fields:
            product.fotografia_url = (fields["fotografia_url"] or "").strip() or None
        if "color_estilo" in fields:
            product.color_estilo = (fields["color_estilo"] or "").strip() or None
        if "codigo_barras" in fields:
            product.codigo_barras = (fields["codigo_barras"] or "").strip() or None
        if "precio_base" in fields:
            product.precio_base = ProductController._validate_price(
                fields["precio_base"], "precio_base"
            )
        if "iva_porcentaje" in fields:
            product.iva_porcentaje = ProductController._validate_price(
                fields["iva_porcentaje"], "iva_porcentaje"
            )
        if "precio_base" in fields or "iva_porcentaje" in fields:
            product.precio_actual = ProductController._calculate_final_price(
                product.precio_base,
                product.iva_porcentaje,
            )
        if "stock" in fields:
            product.stock = ProductController._validate_stock(fields["stock"])
        if "activo" in fields:
            product.activo = bool(fields["activo"])

        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def delete_product(product: Product) -> None:
        """Elimina un producto del catalogo."""

        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def _validate_name(value: str) -> str:
        """Exige un nombre no vacio para el producto."""

        name = (value or "").strip()
        if not name:
            raise ValueError("nombre es obligatorio")
        return name

    @staticmethod
    def _validate_unique_name(value: str, current_product_id: int | None = None) -> None:
        # SQL Server commonly runs under case-insensitive collation, so a direct
        # equality comparison avoids driver issues from LOWER(...) while preserving
        # the uniqueness rule in practice for this deployment target.
        query = Product.query.filter(Product.nombre == value)
        if current_product_id is not None:
            query = query.filter(Product.id_producto != current_product_id)
        if query.first() is not None:
            raise ValueError("ya existe un producto con ese nombre")

    @staticmethod
    def _validate_price(value, field_name: str) -> Decimal:
        """Valida montos numericos y los normaliza a dos decimales."""

        try:
            price = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} debe ser numerico") from exc
        if price <= 0:
            raise ValueError(f"{field_name} debe ser mayor a cero")
        return price.quantize(Decimal("0.01"))

    @staticmethod
    def _validate_stock(value) -> int:
        """Valida que el stock sea un entero no negativo."""

        try:
            stock = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("stock debe ser numerico") from exc
        if stock < 0:
            raise ValueError("stock no puede ser negativo")
        return stock

    @staticmethod
    def _calculate_final_price(precio_base: Decimal, iva_porcentaje: Decimal) -> Decimal:
        """Calcula el precio actual aplicando el IVA sobre el precio base."""

        multiplier = Decimal("1.00") + (iva_porcentaje / Decimal("100.00"))
        return (precio_base * multiplier).quantize(Decimal("0.01"))
