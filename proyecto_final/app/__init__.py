"""Punto de entrada principal de la aplicacion Flask.

Este modulo crea la aplicacion, carga la configuracion del entorno,
inicializa la base de datos y registra los blueprints del frontend y del API.
"""

from flask import Flask

from app.config import Config
from app.database import db
from app.db_bootstrap import bootstrap_database
from app.routes.api_v1 import api_v1_bp
from app.routes.frontend import frontend_bp


def create_app() -> Flask:
    """Construye y devuelve la aplicacion Flask completamente configurada."""

    app = Flask(__name__, template_folder="views/templates")
    app.config.from_object(Config)

    # The schema/seed bootstrap is only enabled for controlled environments such as
    # local setup; normal app startup should work without elevated DB permissions.
    if app.config.get("BOOTSTRAP_DATABASE"):
        bootstrap_database(
            db_user=app.config["DB_USER"],
            db_password=app.config["DB_PASSWORD"],
            db_host=app.config["DB_HOST"],
            db_port=app.config["DB_PORT"],
            db_name=app.config["DB_NAME"],
            db_driver=app.config["DB_DRIVER"],
        )

    db.init_app(app)
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(frontend_bp)

    return app
