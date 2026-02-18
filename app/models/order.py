from app.database import db


class Order(db.Model):
    __tablename__ = "Orden_Compra"

    id_orden = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(20), nullable=False)
