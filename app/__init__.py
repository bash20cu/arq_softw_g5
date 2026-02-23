from flask import Flask

from app.config import Config
from app.database import db
from app.routes.api_v1 import api_v1_bp
from app.routes.routes import main

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(api_v1_bp)
    app.register_blueprint(main)
    return app
