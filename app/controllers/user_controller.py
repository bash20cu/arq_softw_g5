from app.models.user import User


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
