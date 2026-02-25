from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text


def _build_server_uri(user: str, password: str, host: str, port: str) -> str:
    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/"


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
    engine = create_engine(server_uri)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT 1 FROM INFORMATION_SCHEMA.SCHEMATA "
                "WHERE SCHEMA_NAME = :db_name LIMIT 1"
            ),
            {"db_name": db_name},
        )
        return result.scalar() is not None


def run_sql_file(server_uri: str, sql_file: Path, db_name: str | None = None) -> None:
    engine = create_engine(server_uri)
    statements = _read_statements(sql_file, db_name=db_name)
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
    server_uri = _build_server_uri(db_user, db_password, db_host, db_port)
    if _database_exists(server_uri, db_name):
        return

    root_dir = Path(__file__).resolve().parents[1]
    sql_dir = root_dir / "app" / "models"
    schema_path = sql_dir / "schema.sql"
    seed_path = sql_dir / "seed.sql"

    run_sql_file(server_uri, schema_path, db_name=db_name)
    run_sql_file(server_uri, seed_path, db_name=db_name)
