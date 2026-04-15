"""Controlador de autenticacion.

Su objetivo es delegar la validacion de credenciales y construir la identidad
reducida que se guarda en la sesion HTTP.
"""

from app.controllers.user_controller import UserController


class AuthController:
    @staticmethod
    def verify_credentials(username: str, password: str):
        """Valida credenciales usando la logica del controlador de usuarios."""

        return UserController.verify_credentials(username=username, plain_password=password)

    @staticmethod
    def build_session_user(user) -> dict:
        """Construye el payload minimo que se persiste en sesion."""

        # Store only the minimum identity data required for authorization checks.
        return {
            "id_usuario": user.id_usuario,
            "username": user.username,
            "cedula_persona": user.cedula_persona,
            "id_rol": user.id_rol,
        }
