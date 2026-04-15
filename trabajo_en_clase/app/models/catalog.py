from app.database import db


class Role(db.Model):
    __tablename__ = "rol"

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id_rol": self.id_rol,
            "nombre_rol": self.nombre_rol,
        }


class Provincia(db.Model):
    __tablename__ = "provincia"

    id_provincia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id_provincia": self.id_provincia,
            "nombre": self.nombre,
        }


class Canton(db.Model):
    __tablename__ = "canton"

    id_canton = db.Column(db.Integer, primary_key=True)
    id_provincia = db.Column(db.Integer, db.ForeignKey("provincia.id_provincia"), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)

    provincia = db.relationship("Provincia", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id_canton": self.id_canton,
            "id_provincia": self.id_provincia,
            "nombre": self.nombre,
        }


class Distrito(db.Model):
    __tablename__ = "distrito"

    id_distrito = db.Column(db.Integer, primary_key=True)
    id_canton = db.Column(db.Integer, db.ForeignKey("canton.id_canton"), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)

    canton = db.relationship("Canton", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id_distrito": self.id_distrito,
            "id_canton": self.id_canton,
            "nombre": self.nombre,
        }
