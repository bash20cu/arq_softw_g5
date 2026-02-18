import os
from pathlib import Path

import pymysql
import pytest
from flask import Flask
from dotenv import load_dotenv

from app.database import db
from app.models.order import Order
from app.models.support_case import SupportCase
from app.models.user import User
from app.routes.api_v1 import api_v1_bp

load_dotenv()


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
            User(
                cedula_persona="101110111",
                username="miguel_admin",
                password_hash="admin123",
                id_rol=1,
                activo=True,
            )
        )
        db.session.add(
            User(
                cedula_persona="202220222",
                username="carlo_ventas",
                password_hash="ventas123",
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


def _execute_sql_file(cursor, sql_path: Path):
    raw = sql_path.read_text(encoding="utf-8")
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
    db_host = os.getenv("MYSQL_HOST", "localhost")
    db_port = int(os.getenv("MYSQL_PORT", "3306"))
    db_user = os.getenv("MYSQL_USER", "root")
    db_password = os.getenv("MYSQL_PASSWORD", "")

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
        root = Path(__file__).resolve().parents[1]
        _execute_sql_file(cursor, root / "sql" / "schema.sql")
        _execute_sql_file(cursor, root / "sql" / "seed.sql")
        cursor.close()
    finally:
        conn.close()

    from app import create_app

    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client
