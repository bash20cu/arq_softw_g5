from app.models.user import User
from werkzeug.security import check_password_hash


class UserController:
    @staticmethod
    def list_users() -> list[User]:
        return User.query.order_by(User.id_usuario.asc()).all()

    @staticmethod
    def create_user(
        cedula_persona: str,
        username: str,
        password_hash: str,
        id_rol: int,
        activo: bool = True,
    ) -> User:
        user = User(
            cedula_persona=cedula_persona,
            username=username,
            password_hash=password_hash,
            id_rol=id_rol,
            activo=activo,
        )
        user.save()
        return user

    @staticmethod
    def verify_credentials(username: str, plain_password: str) -> User | None:
        user = User.query.filter_by(username=username, activo=True).first()
        if user is None:
            return None

        stored = user.password_hash or ""

        # Allow either Werkzeug-hashed passwords or plain text during early development.
        if stored.startswith(("pbkdf2:", "scrypt:")):
            if check_password_hash(stored, plain_password):
                return user
            return None

        if stored == plain_password:
            return user

        return None
