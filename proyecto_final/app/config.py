import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
import pyodbc

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "si", "yes", "on"}


def _resolve_sql_driver(preferred_driver: str) -> str:
    """Pick the configured SQL Server driver when installed, otherwise fall back safely."""

    requested = preferred_driver.strip()
    installed = {driver.strip() for driver in pyodbc.drivers()}
    if requested in installed:
        return requested
    if "SQL Server" in installed:
        return "SQL Server"
    return requested


class Config:
    SECRET_KEY = _require_env("SECRET_KEY")
    DB_HOST = _require_env("MSSQL_HOST")
    DB_PORT = _require_env("MSSQL_PORT")
    DB_NAME = _require_env("MSSQL_DB")
    DB_USER = _require_env("MSSQL_USER")
    DB_PASSWORD = _require_env("MSSQL_PASSWORD")
    DB_DRIVER = _resolve_sql_driver(_require_env("MSSQL_DRIVER"))
    # Keep database bootstrap explicit so production/runtime startup does not require
    # database creation permissions.
    BOOTSTRAP_DATABASE = _get_bool_env("BOOTSTRAP_DATABASE", default=False)

    # Older Windows "SQL Server" ODBC drivers reject TrustServerCertificate, so we
    # only append it when a newer driver is configured.
    _query_params = [f"driver={quote_plus(DB_DRIVER)}"]
    if DB_DRIVER.strip().lower() != "sql server":
        _query_params.append("TrustServerCertificate=yes")

    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://"
        f"{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@"
        f"{DB_HOST}:{DB_PORT}/{quote_plus(DB_NAME)}"
        f"?{'&'.join(_query_params)}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
