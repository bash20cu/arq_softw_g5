"""Modelos de catalogos auxiliares.

Representan datos relativamente estaticos usados por formularios y reglas
de seguridad, como roles y ubicaciones geograficas.
"""

from app.database import db


class Role(db.Model):
    """Rol de seguridad del sistema."""

    __tablename__ = "rol"

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self) -> dict:
        """Serializa el rol en un formato amigable para JSON."""

        return {
            "id_rol": self.id_rol,
            "nombre_rol": self.nombre_rol,
        }


class Provincia(db.Model):
    """Provincia del catalogo geografico."""

    __tablename__ = "provincia"

    id_provincia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def to_dict(self) -> dict:
        """Serializa la provincia para respuestas JSON."""

        return {
            "id_provincia": self.id_provincia,
            "nombre": self.nombre,
        }


class Canton(db.Model):
    """Canton perteneciente a una provincia."""

    __tablename__ = "canton"

    id_canton = db.Column(db.Integer, primary_key=True)
    id_provincia = db.Column(db.Integer, db.ForeignKey("provincia.id_provincia"), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)

    provincia = db.relationship("Provincia", lazy="joined")

    def to_dict(self) -> dict:
        """Serializa el canton con su provincia asociada."""

        return {
            "id_canton": self.id_canton,
            "id_provincia": self.id_provincia,
            "nombre": self.nombre,
        }


class Distrito(db.Model):
    """Distrito perteneciente a un canton."""

    __tablename__ = "distrito"

    id_distrito = db.Column(db.Integer, primary_key=True)
    id_canton = db.Column(db.Integer, db.ForeignKey("canton.id_canton"), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)

    canton = db.relationship("Canton", lazy="joined")

    def to_dict(self) -> dict:
        """Serializa el distrito para consumo del frontend."""

        return {
            "id_distrito": self.id_distrito,
            "id_canton": self.id_canton,
            "nombre": self.nombre,
        }
