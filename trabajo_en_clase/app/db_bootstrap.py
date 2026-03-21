from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text


def _build_server_uri(user: str, password: str, host: str, port: str) -> str:
    return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/"


def _read_statements(sql_file: Path, db_name: str | None = None) -> list[str]:
    raw = sql_file.read_text(encoding="utf-8")
    if db_name:
        raw = raw.replace("{{DB_NAME}}", db_name)
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    statements = [stmt.strip() for stmt in cleaned.split(";")]
    return [stmt for stmt in statements if stmt]


def _database_exists(server_uri: str, db_name: str) -> bool:
    normalized_name = db_name.strip().lower()
    engine = create_engine(server_uri + "postgres")  # Connect to default postgres db
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT 1 FROM pg_database WHERE lower(datname) = :db_name"
            ),
            {"db_name": normalized_name},
        )
        return result.scalar() is not None


def _table_exists(server_uri: str, db_name: str, table_name: str) -> bool:
    engine = create_engine(server_uri + db_name)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :table_name
                """
            ),
            {"table_name": table_name},
        )
        return result.scalar() is not None


def run_sql_file(server_uri: str, sql_file: Path, db_name: str | None = None) -> None:
    if db_name:
        uri = server_uri + db_name
    else:
        uri = server_uri + "postgres"
    engine = create_engine(uri)
    statements = _read_statements(sql_file, db_name=db_name)
    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)


def run_sql_statements(
    server_uri: str,
    statements: list[str],
    *,
    db_name: str | None = None,
    autocommit: bool = False,
) -> None:
    if db_name:
        uri = server_uri + db_name
    else:
        uri = server_uri + "postgres"

    engine = create_engine(uri, isolation_level="AUTOCOMMIT" if autocommit else None)
    if autocommit:
        with engine.connect() as conn:
            for stmt in statements:
                conn.exec_driver_sql(stmt)
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)


def _ensure_catalogs_seeded(server_uri: str, db_name: str, catalog_seed_path: Path) -> None:
    uri = server_uri + db_name
    engine = create_engine(uri)
    with engine.begin() as conn:
        roles_count = conn.execute(
            text("SELECT COUNT(*) FROM rol")
        ).scalar() or 0
        provincias_count = conn.execute(
            text("SELECT COUNT(*) FROM provincia")
        ).scalar() or 0
        cantones_count = conn.execute(
            text("SELECT COUNT(*) FROM canton")
        ).scalar() or 0
        distritos_count = conn.execute(
            text("SELECT COUNT(*) FROM distrito")
        ).scalar() or 0

    if min(roles_count, provincias_count, cantones_count, distritos_count) > 0:
        return

    run_sql_file(server_uri, catalog_seed_path, db_name=db_name)


def _ensure_client_schema(server_uri: str, db_name: str) -> None:
    uri = server_uri + db_name
    engine = create_engine(uri)
    statements = [
        "ALTER TABLE cliente ALTER COLUMN cedula_persona DROP NOT NULL",
        "ALTER TABLE cliente ALTER COLUMN apellido DROP NOT NULL",
        "ALTER TABLE cliente ADD COLUMN IF NOT EXISTS tipo_cliente VARCHAR(20) NOT NULL DEFAULT 'Persona'",
        "ALTER TABLE cliente ADD COLUMN IF NOT EXISTS nombre VARCHAR(100)",
        "ALTER TABLE cliente ADD COLUMN IF NOT EXISTS apellido VARCHAR(100)",
        "ALTER TABLE cliente ADD COLUMN IF NOT EXISTS email VARCHAR(150)",
        "ALTER TABLE cliente ADD COLUMN IF NOT EXISTS telefono VARCHAR(20)",
        "ALTER TABLE cliente ADD COLUMN IF NOT EXISTS id_distrito INTEGER",
        "UPDATE cliente SET tipo_cliente = COALESCE(tipo_cliente, 'Persona')",
        """
        UPDATE cliente AS c
        SET
            nombre = COALESCE(c.nombre, p.nombre),
            apellido = COALESCE(c.apellido, p.apellido),
            email = COALESCE(c.email, p.email),
            telefono = COALESCE(c.telefono, p.telefono),
            id_distrito = COALESCE(c.id_distrito, p.id_distrito)
        FROM persona AS p
        WHERE c.cedula_persona = p.cedula
        """,
        """
        UPDATE cliente
        SET nombre = COALESCE(nombre, 'Cliente ' || id_cliente)
        """,
        """
        UPDATE cliente
        SET apellido = COALESCE(apellido, 'General')
        WHERE COALESCE(tipo_cliente, 'Persona') = 'Persona'
        """,
        """
        UPDATE cliente
        SET email = COALESCE(email, 'cliente' || id_cliente || '@local.invalid')
        """,
        "ALTER TABLE cliente ALTER COLUMN nombre SET NOT NULL",
        "ALTER TABLE cliente ALTER COLUMN email SET NOT NULL",
    ]
    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)


def bootstrap_database(
    *,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: str,
    db_name: str,
) -> None:
    db_name = db_name.strip().lower()
    server_uri = _build_server_uri(db_user, db_password, db_host, db_port)
    root_dir = Path(__file__).resolve().parents[1]
    sql_dir = root_dir / "app" / "models"
    schema_path = sql_dir / "schema.sql"
    seed_path = sql_dir / "seed.sql"
    catalog_seed_path = sql_dir / "catalog_seed.sql"
    schema_statements = _read_statements(schema_path, db_name=db_name)
    server_statements = []
    database_statements = []

    for stmt in schema_statements:
        normalized = stmt.upper()
        if normalized.startswith("DROP DATABASE") or normalized.startswith("CREATE DATABASE"):
            server_statements.append(stmt)
        else:
            database_statements.append(stmt)

    if not _database_exists(server_uri, db_name):
        run_sql_statements(server_uri, server_statements, autocommit=True)
        run_sql_statements(server_uri, database_statements, db_name=db_name)
        run_sql_file(server_uri, seed_path, db_name=db_name)
        return

    if not _table_exists(server_uri, db_name, "rol"):
        run_sql_statements(server_uri, database_statements, db_name=db_name)
        run_sql_file(server_uri, seed_path, db_name=db_name)
        return

    _ensure_client_schema(server_uri, db_name)
    _ensure_catalogs_seeded(server_uri, db_name, catalog_seed_path)
