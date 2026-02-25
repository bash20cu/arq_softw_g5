import os
import sys
from pathlib import Path

import pymysql
import pytest
from flask import Flask
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Permite `import app...` cuando pytest se ejecuta desde `tests/`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import db
from app.models.order import Order
from app.models.support_case import SupportCase
from app.models.user import Persona, User
from app.routes.api_v1 import api_v1_bp

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable for tests: {name}")
    return value


@pytest.fixture()
def app(tmp_path: Path):
    db_path = tmp_path / "test_backend.db"

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

        db.session.add(
            Persona(
                cedula="101110111",
                nombre="Miguel",
                apellido="Admin",
                email="miguel_admin_test@enviosg5.com",
                telefono="88880001",
            )
        )
        db.session.add(
            Persona(
                cedula="202220222",
                nombre="Carlo",
                apellido="Vargas",
                email="carlo_ventas_test@enviosg5.com",
                telefono="88880002",
            )
        )
        db.session.add(
            Persona(
                cedula="404440444",
                nombre="Laura",
                apellido="Campos",
                email="laura_campos_test@enviosg5.com",
                telefono="88880004",
            )
        )
        db.session.add(
            Persona(
                cedula="505550555",
                nombre="Q",
                apellido="User",
                email="qa_user_test@enviosg5.com",
                telefono="88880005",
            )
        )
        db.session.add(
            Persona(
                cedula="606660666",
                nombre="Before",
                apellido="Update",
                email="before_update_test@enviosg5.com",
                telefono="88880006",
            )
        )
        db.session.add(
            Persona(
                cedula="707770777",
                nombre="To",
                apellido="Delete",
                email="to_delete_test@enviosg5.com",
                telefono="88880007",
            )
        )
        db.session.add(
            Persona(
                cedula="909990999",
                nombre="Nuevo",
                apellido="Publico",
                email="nuevo_publico_test@enviosg5.com",
                telefono="88880009",
            )
        )

        db.session.add(
            User(
                cedula_persona="101110111",
                username="miguel_admin",
                password_hash=generate_password_hash("admin123"),
                id_rol=1,
                activo=True,
            )
        )
        db.session.add(
            User(
                cedula_persona="202220222",
                username="carlo_ventas",
                password_hash=generate_password_hash("ventas123"),
                id_rol=2,
                activo=True,
            )
        )

        db.session.add_all(
            [
                Order(estado="Pendiente"),
                Order(estado="Pendiente"),
                Order(estado="Enviado"),
                Order(estado="Procesado"),
            ]
        )

        db.session.add_all(
            [
                SupportCase(estado="Nuevo"),
                SupportCase(estado="En Análisis"),
                SupportCase(estado="Resuelto"),
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


def _execute_sql_file(cursor, sql_path: Path, db_name: str):
    raw = sql_path.read_text(encoding="utf-8")
    raw = raw.replace("{{DB_NAME}}", db_name)
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        lines.append(line)
    statements = [stmt.strip() for stmt in "\n".join(lines).split(";") if stmt.strip()]
    for stmt in statements:
        cursor.execute(stmt)


@pytest.fixture()
def real_client():
    db_host = _require_env("MYSQL_HOST")
    db_port = int(_require_env("MYSQL_PORT"))
    db_user = _require_env("MYSQL_USER")
    db_password = _require_env("MYSQL_PASSWORD")
    db_name = _require_env("MYSQL_DATABASE")

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            autocommit=True,
        )
    except Exception as exc:
        pytest.skip(f"MySQL no disponible para integration tests: {exc}")

    try:
        cursor = conn.cursor()
        sql_dir = PROJECT_ROOT / "app" / "models"
        _execute_sql_file(cursor, sql_dir / "schema.sql", db_name)
        _execute_sql_file(cursor, sql_dir / "seed.sql", db_name)
        cursor.close()
    finally:
        conn.close()

    mysql_uri = (
        "mysql+pymysql://"
        f"{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI=mysql_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    app.register_blueprint(api_v1_bp)

    with app.test_client() as client:
        yield client
