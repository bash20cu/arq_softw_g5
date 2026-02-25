from flask import Flask

from app.config import Config
from app.database import db
from app.db_bootstrap import bootstrap_database
from app.routes.api_v1 import api_v1_bp
from app.routes.routes import main

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

<<<<<<< HEAD
    
    print("DB URI en runtime:", app.config['SQLALCHEMY_DATABASE_URI'])
=======
    bootstrap_database(
        db_user=app.config["DB_USER"],
        db_password=app.config["DB_PASSWORD"],
        db_host=app.config["DB_HOST"],
        db_port=app.config["DB_PORT"],
        run_schema=app.config["AUTO_DB_SCHEMA_ON_START"],
        run_seed=app.config["AUTO_DB_SEED_ON_START"],
    )
>>>>>>> developer

    db.init_app(app)

    app.register_blueprint(api_v1_bp)
    app.register_blueprint(main)
    return app