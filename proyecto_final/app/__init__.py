from flask import Flask

from app.config import Config
from app.database import db
from app.db_bootstrap import bootstrap_database


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    bootstrap_database(
        db_user=app.config["DB_USER"],
        db_password=app.config["DB_PASSWORD"],
        db_host=app.config["DB_HOST"],
        db_port=app.config["DB_PORT"],
        db_name=app.config["DB_NAME"],
        db_driver=app.config["DB_DRIVER"],
    )

    db.init_app(app)

    return app
