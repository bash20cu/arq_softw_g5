from flask import Flask
from app.config import Config


def create_app():
    app = Flask(
        __name__,
        template_folder='views/templates',
        static_folder='views/static'
    )
    app.config.from_object(Config)

    # Blueprint de tus compañeros (API JSON → /api/v1/...)
    from app.routes.api_v1 import api_v1_bp
    app.register_blueprint(api_v1_bp)

    # Blueprint del frontend (pantallas HTML → /usuarios/...)
    from app.routes.frontend import frontend_bp
    app.register_blueprint(frontend_bp)

    # Redirigir raíz a la lista de usuarios
    from flask import redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('frontend.usuarios_listar'))

    return app