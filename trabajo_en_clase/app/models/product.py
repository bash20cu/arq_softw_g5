from app.database import db


class Product(db.Model):
    __tablename__ = "producto"

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    precio_actual = db.Column(db.Numeric(12, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    id_campania = db.Column(db.Integer, db.ForeignKey("campania.id_campania"), nullable=True)

    detalles = db.relationship("OrderDetail", back_populates="producto", lazy="selectin")
    campania = db.relationship("Campaign", back_populates="productos", lazy="joined")

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio_actual": float(self.precio_actual),
            "stock": self.stock,
            "id_campania": self.id_campania,
            "nombre_campania": self.campania.nombre if self.campania else None,
        }
