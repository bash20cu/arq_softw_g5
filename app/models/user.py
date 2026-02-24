from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "Usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    cedula_persona = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password: str) -> None:
        """Genera y guarda el hash seguro de la contraseña"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Valida la contraseña contra el hash almacenado"""
        return check_password_hash(self.password_hash, password)

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
