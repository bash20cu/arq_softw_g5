from flask import Flask
from app.config import Config
from app.database import db
from app.db_bootstrap import bootstrap_database
from app.routes.api_v1 import api_v1_bp

def create_app():
    app = Flask(
        __name__,
        template_folder='views/templates',
        static_folder='views/static'
    )
    app.config.from_object(Config)

    bootstrap_database(
        db_user=app.config["DB_USER"],
        db_password=app.config["DB_PASSWORD"],
        db_host=app.config["DB_HOST"],
        db_port=app.config["DB_PORT"],
        run_schema=app.config["AUTO_DB_SCHEMA_ON_START"],
        run_seed=app.config["AUTO_DB_SEED_ON_START"],
    )

    db.init_app(app)

    app.register_blueprint(api_v1_bp)

    # Blueprint del frontend (pantallas HTML)
    from app.routes.frontend import frontend_bp
    app.register_blueprint(frontend_bp)

    from flask import redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('frontend.usuarios_listar'))

    return app