from app.database import db


class SupportCase(db.Model):
    __tablename__ = "caso_soporte"

    id_caso = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(30), nullable=False)
