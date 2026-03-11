from datetime import datetime

from app.database import db


class Order(db.Model):
    __tablename__ = "Orden_Compra"

    id_orden = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    fecha_orden = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Pendiente")

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
            "fecha_orden": self.fecha_orden.isoformat() if self.fecha_orden else None,
            "estado": self.estado,
        }
        if include_details:
            payload["detalles"] = [detalle.to_dict() for detalle in self.detalles]
        return payload


class OrderDetail(db.Model):
    __tablename__ = "Detalle_Orden"

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_orden = db.Column(db.Integer, db.ForeignKey("Orden_Compra.id_orden"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("Producto.id_producto"), nullable=False)
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
