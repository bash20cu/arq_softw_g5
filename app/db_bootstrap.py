from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine


def _build_server_uri(user: str, password: str, host: str, port: str) -> str:
    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/"


def _read_statements(sql_file: Path) -> list[str]:
    raw = sql_file.read_text(encoding="utf-8")
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    statements = [stmt.strip() for stmt in cleaned.split(";")]
    return [stmt for stmt in statements if stmt]


def run_sql_file(server_uri: str, sql_file: Path) -> None:
    engine = create_engine(server_uri)
    statements = _read_statements(sql_file)
    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)


def bootstrap_database(
    *,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: str,
    run_schema: bool,
    run_seed: bool,
) -> None:
    if not run_schema and not run_seed:
        return

    root_dir = Path(__file__).resolve().parents[1]
    sql_dir = root_dir / "database" / "docker-entrypoint-initdb.d"
    schema_path = sql_dir / "schema.sql"
    seed_path = sql_dir / "seed.sql"
    server_uri = _build_server_uri(db_user, db_password, db_host, db_port)

    if run_schema:
        run_sql_file(server_uri, schema_path)

    if run_seed:
        run_sql_file(server_uri, seed_path)
