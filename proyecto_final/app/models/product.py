from app.database import db


class Product(db.Model):
    __tablename__ = "producto"

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    fotografia_url = db.Column(db.String(255), nullable=True)
    color_estilo = db.Column(db.String(150), nullable=True)
    codigo_barras = db.Column(db.String(80), nullable=True)
    precio_base = db.Column(db.Numeric(12, 2), nullable=False)
    iva_porcentaje = db.Column(db.Numeric(5, 2), nullable=False, default=13.00)
    precio_actual = db.Column(db.Numeric(12, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    detalles = db.relationship("OrderDetail", back_populates="producto", lazy="selectin")

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fotografia_url": self.fotografia_url,
            "color_estilo": self.color_estilo,
            "codigo_barras": self.codigo_barras,
            "precio_base": float(self.precio_base),
            "iva_porcentaje": float(self.iva_porcentaje),
            "precio_actual": float(self.precio_actual),
            "stock": self.stock,
            "activo": self.activo,
        }
