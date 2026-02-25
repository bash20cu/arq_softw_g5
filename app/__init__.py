from flask import Flask

from app.config import Config
from app.database import db
from app.db_bootstrap import bootstrap_database
from app.routes.api_v1 import api_v1_bp
from app.routes.routes import main


def create_app() -> Flask:
    app = Flask(__name__, template_folder="Templates")
    app.config.from_object(Config)

    bootstrap_database(
        db_user=app.config["DB_USER"],
        db_password=app.config["DB_PASSWORD"],
        db_host=app.config["DB_HOST"],
        db_port=app.config["DB_PORT"],
        db_name=app.config["DB_NAME"],
    )

    db.init_app(app)

    app.register_blueprint(api_v1_bp)
    app.register_blueprint(main)

    # Frontend CRUD de usuarios (templates HTML).
    from app.routes.frontend import frontend_bp

    app.register_blueprint(frontend_bp)
    return app
