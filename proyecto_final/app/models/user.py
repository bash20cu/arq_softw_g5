"""Modelos relacionados con personas, usuarios, clientes y facturas."""

from datetime import datetime

from app.database import db
from werkzeug.security import check_password_hash, generate_password_hash


def _serialize_datetime(value):
    """Convierte fechas a texto ISO o conserva el valor textual recibido del driver."""

    # SQL Server can occasionally materialize DATETIME values as strings depending
    # on driver behavior, so user-facing payloads normalize both representations.
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


class Persona(db.Model):
    """Entidad base de persona fisica utilizada por usuarios y clientes."""

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
        """Guarda la persona actual en base de datos."""

        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        """Serializa la persona para respuestas JSON."""

        return {
            "cedula": self.cedula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "telefono": self.telefono,
            "id_distrito": self.id_distrito,
            "fecha_registro": _serialize_datetime(self.fecha_registro),
        }


class User(db.Model):
    """Usuario autenticable del sistema."""

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
        """Guarda el usuario actual en base de datos."""

        db.session.add(self)
        db.session.commit()

    def to_dict(self) -> dict:
        """Serializa el usuario con datos de rol y persona enlazada."""

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
    """Cliente comercial que puede o no estar vinculado a una Persona."""

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
        """Devuelve el nombre a mostrar segun el tipo de cliente."""

        if self.tipo_cliente == "Empresa":
            return self.nombre
        return f"{self.nombre} {self.apellido}".strip()

    def save(self):
        """Guarda el cliente actual en base de datos."""

        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Serializa el cliente para consumo del API."""

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
    """Factura emitida por el sistema."""

    __tablename__ = "factura"

    id_factura = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    monto_total = db.Column(db.Float, nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False)

    def save(self):
        """Guarda la factura actual en base de datos."""

        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Serializa la factura para respuestas JSON."""

        return {
            "id_factura": self.id_factura,
            "numero_factura": self.numero_factura,
            "monto_total": self.monto_total,
            "fecha_emision": _serialize_datetime(self.fecha_emision),
        }
