from app.controllers.user_controller import UserController


class AuthController:
    @staticmethod
    def verify_credentials(username: str, password: str):
        return UserController.verify_credentials(username=username, plain_password=password)

    @staticmethod
    def build_session_user(user) -> dict:
        return {
            "id_usuario": user.id_usuario,
            "username": user.username,
            "id_rol": user.id_rol,
        }
