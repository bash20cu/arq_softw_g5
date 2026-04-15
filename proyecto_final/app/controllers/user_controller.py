"""Controlador de usuarios del sistema.

Se encarga del CRUD de usuarios y de la verificacion de credenciales usando
hashes seguros de contrasena.
"""

from app.models.user import Persona, User
from werkzeug.security import check_password_hash, generate_password_hash


class UserController:
    @staticmethod
    def _ensure_password_hash(password_value: str) -> str:
        """Convierte una contrasena plana en hash o acepta un hash ya generado."""

        value = (password_value or "").strip()
        if not value:
            raise ValueError("password no puede estar vacio")

        if value.startswith(("pbkdf2:", "scrypt:")):
            return value
        return generate_password_hash(value)

    @staticmethod
    def list_users() -> list[User]:
        """Lista todos los usuarios registrados."""

        return User.query.order_by(User.id_usuario.asc()).all()

    @staticmethod
    def list_personas_for_user(current_cedula: str | None = None) -> list[Persona]:
        """Devuelve personas disponibles para crear o reasignar usuarios."""

        used_cedulas = {item.cedula_persona for item in User.query.all()}
        query = Persona.query
        if current_cedula:
            used_cedulas.discard(current_cedula)
        if used_cedulas:
            query = query.filter(~Persona.cedula.in_(used_cedulas))
        return query.order_by(Persona.nombre.asc(), Persona.apellido.asc()).all()

    @staticmethod
    def create_user(
        cedula_persona: str,
        username: str,
        password_hash: str,
        id_rol: int,
        activo: bool = True,
    ) -> User:
        """Crea un usuario validando primero la Persona asociada."""

        if Persona.query.filter_by(cedula=cedula_persona).first() is None:
            raise ValueError("cedula_persona no existe en Persona")
        user = User(
            cedula_persona=cedula_persona,
            username=username,
            password_hash=UserController._ensure_password_hash(password_hash),
            id_rol=id_rol,
            activo=activo,
        )
        user.save()
        return user

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """Busca un usuario por nombre de acceso."""

        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_cedula(cedula_persona: str) -> User | None:
        """Busca un usuario por la cedula de la persona vinculada."""

        return User.query.filter_by(cedula_persona=cedula_persona).first()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """Busca un usuario por su id interno."""

        return User.query.filter_by(id_usuario=user_id).first()

    @staticmethod
    def update_user(user: User, **fields) -> User:
        """Actualiza un usuario y rehace el hash si cambia la contrasena."""

        if "cedula_persona" in fields:
            if Persona.query.filter_by(cedula=fields["cedula_persona"]).first() is None:
                raise ValueError("cedula_persona no existe en Persona")
            user.cedula_persona = fields["cedula_persona"]
        if "username" in fields:
            user.username = fields["username"]
        if "password_hash" in fields:
            user.password_hash = UserController._ensure_password_hash(
                fields["password_hash"]
            )
        if "id_rol" in fields:
            user.id_rol = fields["id_rol"]
        if "activo" in fields:
            user.activo = fields["activo"]

        user.save()
        return user

    @staticmethod
    def delete_user(user: User) -> None:
        """Elimina un usuario del sistema."""

        from app.database import db

        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def verify_credentials(username: str, plain_password: str) -> User | None:
        """Valida credenciales contra el hash almacenado en base de datos."""

        user = User.query.filter_by(username=username, activo=True).first()
        if user is None:
            return None

        stored = user.password_hash or ""
        if not stored.startswith(("pbkdf2:", "scrypt:")):
            return None
        if check_password_hash(stored, plain_password):
            return user
        return None
