import os
import sys
from datetime import date
from pathlib import Path

import psycopg2
import pytest
from flask import Flask
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Permite `import app...` cuando pytest se ejecuta desde `tests/`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import db
from app.models.catalog import Canton, Distrito, Provincia, Role
from app.models.campaign import Campaign
from app.models.order import Order, OrderDetail
from app.models.product import Product
from app.models.support_case import SupportCase
from app.models.user import Cliente, Persona, User
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

        db.session.add(Role(id_rol=1, nombre_rol="Admin"))
        db.session.add(Role(id_rol=2, nombre_rol="Vendedor"))
        db.session.add(Role(id_rol=3, nombre_rol="Soporte"))
        db.session.add(Role(id_rol=4, nombre_rol="Cliente"))
        db.session.add(Provincia(id_provincia=1, nombre="San Jose"))
        db.session.add(Canton(id_canton=101, id_provincia=1, nombre="Central"))
        db.session.add(Distrito(id_distrito=10101, id_canton=101, nombre="Catedral"))

        db.session.add(
            Persona(
                cedula="101110111",
                nombre="Miguel",
                apellido="Admin",
                email="miguel_admin_test@enviosg5.com",
                telefono="88880001",
                id_distrito=10101,
            )
        )
        db.session.add(
            Persona(
                cedula="202220222",
                nombre="Carlo",
                apellido="Vargas",
                email="carlo_ventas_test@enviosg5.com",
                telefono="88880002",
                id_distrito=10101,
            )
        )
        db.session.add(
            Persona(
                cedula="404440444",
                nombre="Laura",
                apellido="Campos",
                email="laura_campos_test@enviosg5.com",
                telefono="88880004",
                id_distrito=10101,
            )
        )
        db.session.add(
            Persona(
                cedula="505550555",
                nombre="Q",
                apellido="User",
                email="qa_user_test@enviosg5.com",
                telefono="88880005",
                id_distrito=10101,
            )
        )
        db.session.add(
            Persona(
                cedula="606660666",
                nombre="Before",
                apellido="Update",
                email="before_update_test@enviosg5.com",
                telefono="88880006",
                id_distrito=10101,
            )
        )
        db.session.add(
            Persona(
                cedula="707770777",
                nombre="To",
                apellido="Delete",
                email="to_delete_test@enviosg5.com",
                telefono="88880007",
                id_distrito=10101,
            )
        )
        db.session.add(
            Persona(
                cedula="909990999",
                nombre="Nuevo",
                apellido="Publico",
                email="nuevo_publico_test@enviosg5.com",
                telefono="88880009",
                id_distrito=10101,
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
                Cliente(
                    id_cliente=1,
                    cedula_persona="202220222",
                    nombre="Carlo",
                    apellido="Vargas",
                    email="carlo_ventas_test@enviosg5.com",
                    telefono="88880002",
                    id_distrito=10101,
                ),
                Cliente(
                    id_cliente=2,
                    cedula_persona="909990999",
                    nombre="Nuevo",
                    apellido="Publico",
                    email="nuevo_publico_test@enviosg5.com",
                    telefono="88880009",
                    id_distrito=10101,
                ),
            ]
        )

        db.session.add_all(
            [
                Campaign(
                    id_campania=1,
                    nombre="Promo Envio Express",
                    fecha_inicio=date(2026, 2, 1),
                    fecha_fin=date(2026, 3, 15),
                    descripcion="Descuento para envios urgentes.",
                ),
                Campaign(
                    id_campania=2,
                    nombre="Temporada Escolar",
                    fecha_inicio=date(2026, 3, 1),
                    fecha_fin=date(2026, 4, 30),
                    descripcion="Campaña comercial para paquetes escolares.",
                ),
            ]
        )

        db.session.add_all(
            [
                Product(
                    id_producto=1,
                    nombre="Envio Nacional Estandar",
                    precio_actual=3500.00,
                    stock=500,
                    id_campania=1,
                ),
                Product(
                    id_producto=2,
                    nombre="Envio Internacional Express",
                    precio_actual=18500.00,
                    stock=120,
                    id_campania=2,
                ),
                Product(
                    id_producto=3,
                    nombre="Seguro Premium",
                    precio_actual=2500.00,
                    stock=50,
                    id_campania=None,
                ),
            ]
        )

        db.session.add_all(
            [
                Order(id_orden=1, id_cliente=1, id_usuario=2, estado="Pendiente"),
                Order(id_orden=2, id_cliente=1, id_usuario=2, estado="Pendiente"),
                Order(id_orden=3, id_cliente=1, id_usuario=2, estado="Enviado"),
                Order(id_orden=4, id_cliente=1, id_usuario=2, estado="Procesado"),
            ]
        )

        db.session.add_all(
            [
                OrderDetail(
                    id_detalle=1,
                    id_orden=1,
                    id_producto=1,
                    cantidad=1,
                    precio_venta=3500.00,
                ),
                OrderDetail(
                    id_detalle=2,
                    id_orden=2,
                    id_producto=2,
                    cantidad=1,
                    precio_venta=18500.00,
                ),
                OrderDetail(
                    id_detalle=3,
                    id_orden=3,
                    id_producto=1,
                    cantidad=2,
                    precio_venta=3500.00,
                ),
                OrderDetail(
                    id_detalle=4,
                    id_orden=4,
                    id_producto=3,
                    cantidad=2,
                    precio_venta=2500.00,
                ),
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
    db_host = _require_env("POSTGRES_HOST")
    db_port = int(_require_env("POSTGRES_PORT"))
    db_user = _require_env("POSTGRES_USER")
    db_password = _require_env("POSTGRES_PASSWORD")
    db_name = _require_env("POSTGRES_DB")

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres",  # Connect to default db first
        )
        conn.autocommit = True
    except Exception as exc:
        pytest.skip(f"PostgreSQL no disponible para integration tests: {exc}")

    try:
        cursor = conn.cursor()
        # Create database if it doesn't exist
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.close()
        conn.close()

        # Connect to the specific database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        conn.autocommit = True
        cursor = conn.cursor()
        sql_dir = PROJECT_ROOT / "app" / "models"
        _execute_sql_file(cursor, sql_dir / "schema.sql", db_name)
        _execute_sql_file(cursor, sql_dir / "seed.sql", db_name)
        cursor.close()
    finally:
        conn.close()

    postgres_uri = (
        "postgresql://"
        f"{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI=postgres_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    app.register_blueprint(api_v1_bp)

    with app.test_client() as client:
        yield client
