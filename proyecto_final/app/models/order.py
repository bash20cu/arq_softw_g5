from datetime import datetime

from app.database import db


def _serialize_datetime(value):
    # Some SQL Server / ODBC combinations can hand back datetime columns as strings,
    # so the API serializer needs to tolerate both Python datetime objects and text.
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


class Order(db.Model):
    __tablename__ = "orden_compra"

    id_orden = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_orden = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(40), nullable=False, default="En preparacion")

    cliente = db.relationship("Cliente", lazy="joined")
    usuario = db.relationship("User", lazy="joined")
    detalles = db.relationship(
        "OrderDetail",
        back_populates="orden",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def to_dict(self, *, include_details: bool = False) -> dict:
        payload = {
            "id_orden": self.id_orden,
            "id_cliente": self.id_cliente,
            "id_usuario": self.id_usuario,
            "fecha_orden": _serialize_datetime(self.fecha_orden),
            "estado": self.estado,
            "nombre_cliente": self.cliente.nombre_completo if self.cliente else None,
            "nombre_usuario": self.usuario.to_dict().get("nombre_persona") if self.usuario else None,
            "username_usuario": self.usuario.username if self.usuario else None,
        }
        if include_details:
            payload["detalles"] = [detalle.to_dict() for detalle in self.detalles]
        return payload


class OrderDetail(db.Model):
    __tablename__ = "detalle_orden"

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey("orden_compra.id_orden"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_venta = db.Column(db.Numeric(12, 2), nullable=False)

    orden = db.relationship("Order", back_populates="detalles")
    producto = db.relationship("Product", back_populates="detalles")

    @property
    def subtotal(self) -> float:
        return float(self.precio_venta) * self.cantidad

    def to_dict(self) -> dict:
        return {
            "id_detalle": self.id_detalle,
            "id_orden": self.id_orden,
            "id_producto": self.id_producto,
            "cantidad": self.cantidad,
            "precio_venta": float(self.precio_venta),
            "subtotal": self.subtotal,
            "producto": self.producto.to_dict() if self.producto else None,
        }


class Payment(db.Model):
    __tablename__ = "pago"

    id_pago = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey("orden_compra.id_orden"), nullable=False)
    proveedor = db.Column(db.String(50), nullable=False)
    referencia_externa = db.Column(db.String(120), nullable=True)
    # Persist the approval URL so a pending PayPal checkout can be resumed later.
    approve_url = db.Column(db.String(500), nullable=True)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    estado = db.Column(db.String(30), nullable=False, default="Pendiente")
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    orden = db.relationship("Order", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id_pago": self.id_pago,
            "id_orden": self.id_orden,
            "proveedor": self.proveedor,
            "referencia_externa": self.referencia_externa,
            "approve_url": self.approve_url,
            "monto": float(self.monto),
            "estado": self.estado,
            "fecha_pago": _serialize_datetime(self.fecha_pago),
        }
