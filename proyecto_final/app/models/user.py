from datetime import datetime

from app.database import db
from werkzeug.security import check_password_hash, generate_password_hash


class Persona(db.Model):
    __tablename__ = "persona"

    cedula = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    id_distrito = db.Column(db.Integer, db.ForeignKey("distrito.id_distrito"), nullable=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    distrito = db.relationship("Distrito", lazy="joined")

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "cedula": self.cedula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "telefono": self.telefono,
            "id_distrito": self.id_distrito,
            "fecha_registro": self.fecha_registro.isoformat()
            if self.fecha_registro
            else None,
        }


class User(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    cedula_persona = db.Column(db.String(20), db.ForeignKey("persona.cedula"), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    persona = db.relationship("Persona", lazy="joined")
    rol = db.relationship("Role", lazy="joined")

    def set_password(self, password: str) -> None:
        """Genera y guarda el hash seguro de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Valida la contraseña contra el hash almacenado."""
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
            "nombre_persona": (
                f"{self.persona.nombre} {self.persona.apellido}" if self.persona else None
            ),
            "nombre_rol": self.rol.nombre_rol if self.rol else None,
            "activo": self.activo,
        }


class Cliente(db.Model):
    __tablename__ = "cliente"

    TIPOS_CLIENTE = {"Persona", "Empresa"}

    id_cliente = db.Column(db.Integer, primary_key=True)
    cedula_persona = db.Column(db.String(20), db.ForeignKey("persona.cedula"), unique=True, nullable=True)
    tipo_cliente = db.Column(db.String(20), nullable=False, default="Persona")
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    id_distrito = db.Column(db.Integer, db.ForeignKey("distrito.id_distrito"), nullable=True)
    puntos_lealtad = db.Column(db.Integer, default=0)
    estado_cliente = db.Column(db.String(20), default="Activo")

    persona = db.relationship("Persona", lazy="joined")
    distrito = db.relationship("Distrito", lazy="joined")

    @property
    def nombre_completo(self) -> str:
        if self.tipo_cliente == "Empresa":
            return self.nombre
        return f"{self.nombre} {self.apellido}".strip()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "cedula_persona": self.cedula_persona,
            "tipo_cliente": self.tipo_cliente,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.nombre_completo,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "id_distrito": self.id_distrito,
            "puntos_lealtad": self.puntos_lealtad,
            "estado_cliente": self.estado_cliente,
        }


class Factura(db.Model):
    __tablename__ = "factura"

    id_factura = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    monto_total = db.Column(db.Float, nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id_factura": self.id_factura,
            "numero_factura": self.numero_factura,
            "monto_total": self.monto_total,
            "fecha_emision": self.fecha_emision.isoformat()
            if self.fecha_emision
            else None,
        }
