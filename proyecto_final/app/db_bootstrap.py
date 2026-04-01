from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text


def _build_database_uri(
    *,
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    driver: str,
) -> str:
    # Match the same driver compatibility rule used by the Flask app config so
    # bootstrap works with both the legacy "SQL Server" driver and Driver 18.
    query_params = [f"driver={quote_plus(driver)}"]
    if driver.strip().lower() != "sql server":
        query_params.append("TrustServerCertificate=yes")

    return (
        "mssql+pyodbc://"
        f"{quote_plus(user)}:{quote_plus(password)}@"
        f"{host}:{port}/{quote_plus(database)}"
        f"?{'&'.join(query_params)}"
    )


def _read_statements(sql_file: Path) -> list[str]:
    raw = sql_file.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in raw.split(";")]
    return [stmt for stmt in statements if stmt]


def _database_exists(master_uri: str, db_name: str) -> bool:
    engine = create_engine(master_uri)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM sys.databases WHERE name = :db_name"),
            {"db_name": db_name},
        )
        return result.scalar() is not None


def _table_exists(database_uri: str, table_name: str) -> bool:
    engine = create_engine(database_uri)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT 1
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = :table_name
                """
            ),
            {"table_name": table_name},
        )
        return result.scalar() is not None


def _run_statements(uri: str, statements: list[str], *, autocommit: bool = False) -> None:
    engine = create_engine(uri, isolation_level="AUTOCOMMIT" if autocommit else None)
    if autocommit:
        with engine.connect() as conn:
            for stmt in statements:
                conn.exec_driver_sql(stmt)
        return

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
    db_driver: str,
) -> None:
    root_dir = Path(__file__).resolve().parents[1]
    sql_dir = root_dir / "app" / "sql"
    schema_path = sql_dir / "schema.sql"
    seed_path = sql_dir / "seed.sql"

    master_uri = _build_database_uri(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database="master",
        driver=db_driver,
    )
    database_uri = _build_database_uri(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name,
        driver=db_driver,
    )

    if not _database_exists(master_uri, db_name):
        create_db = [f"CREATE DATABASE [{db_name}]"]
        _run_statements(master_uri, create_db, autocommit=True)

    schema_statements = _read_statements(schema_path)
    _run_statements(database_uri, schema_statements)

    if not _table_exists(database_uri, "rol"):
        return

    if seed_path.exists():
        seed_statements = _read_statements(seed_path)
        _run_statements(database_uri, seed_statements)
