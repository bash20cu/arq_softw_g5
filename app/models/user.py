from app.database import db


class User(db.Model):
    __tablename__ = "Usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    cedula_persona = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id_usuario": self.id_usuario,
            "cedula_persona": self.cedula_persona,
            "username": self.username,
            "id_rol": self.id_rol,
            "activo": self.activo,
        }
