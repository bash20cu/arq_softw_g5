from app.database import db


class Campaign(db.Model):
    __tablename__ = "Campania"

    id_campania = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)

    productos = db.relationship("Product", back_populates="campania", lazy="selectin")

    def to_dict(self) -> dict:
        return {
            "id_campania": self.id_campania,
            "nombre": self.nombre,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "descripcion": self.descripcion,
        }
