import sys
from pathlib import Path

import pytest
from flask import Flask
from werkzeug.security import generate_password_hash

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import db
from app.models.catalog import Canton, Distrito, Provincia, Role
from app.models.user import Persona, User
from app.routes.api_v1 import api_v1_bp


@pytest.fixture()
def app(tmp_path: Path):
    db_path = tmp_path / "test_proyecto_final.db"

    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    app.register_blueprint(api_v1_bp)

    with app.app_context():
        db.create_all()

        db.session.add_all(
            [
                Role(id_rol=1, nombre_rol="Administrador"),
                Role(id_rol=2, nombre_rol="Empleado"),
                Role(id_rol=3, nombre_rol="Cliente"),
                Provincia(id_provincia=1, nombre="San Jose"),
                Canton(id_canton=101, id_provincia=1, nombre="Central"),
                Distrito(id_distrito=10101, id_canton=101, nombre="Catedral"),
                Persona(
                    cedula="101010101",
                    nombre="Admin",
                    apellido="Equipo5",
                    email="admin@test.local",
                    telefono="88880000",
                    id_distrito=10101,
                ),
                User(
                    cedula_persona="101010101",
                    username="admin",
                    password_hash=generate_password_hash("admin123"),
                    id_rol=1,
                    activo=True,
                ),
            ]
        )
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
