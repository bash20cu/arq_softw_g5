from app.controllers.user_controller import UserController


class AuthController:
    @staticmethod
    def verify_credentials(username: str, password: str):
        return UserController.verify_credentials(username=username, plain_password=password)

    @staticmethod
    def build_session_user(user) -> dict:
        # Store only the minimum identity data required for authorization checks.
        return {
            "id_usuario": user.id_usuario,
            "username": user.username,
            "cedula_persona": user.cedula_persona,
            "id_rol": user.id_rol,
        }
