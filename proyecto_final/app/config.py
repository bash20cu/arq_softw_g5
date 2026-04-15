"""Configuracion central del backend.

Aqui se concentran las variables de entorno requeridas por Flask, SQLAlchemy,
SQL Server y la integracion con PayPal.
"""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

from app.odbc import build_sql_server_query, resolve_sql_driver

load_dotenv()


def _require_env(name: str) -> str:
    """Obtiene una variable obligatoria y falla temprano si falta."""

    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


def _get_bool_env(name: str, default: bool = False) -> bool:
    """Interpreta una variable de entorno textual como booleano."""

    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "si", "yes", "on"}


class Config:
    """Objeto de configuracion consumido por Flask."""

    SECRET_KEY = _require_env("SECRET_KEY")
    DB_HOST = _require_env("MSSQL_HOST")
    DB_PORT = _require_env("MSSQL_PORT")
    DB_NAME = _require_env("MSSQL_DB")
    DB_USER = _require_env("MSSQL_USER")
    DB_PASSWORD = _require_env("MSSQL_PASSWORD")
    DB_DRIVER = resolve_sql_driver(_require_env("MSSQL_DRIVER"))
    # Keep database bootstrap explicit so production/runtime startup does not require
    # database creation permissions.
    BOOTSTRAP_DATABASE = _get_bool_env("BOOTSTRAP_DATABASE", default=False)

    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://"
        f"{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@"
        f"{DB_HOST}:{DB_PORT}/{quote_plus(DB_NAME)}"
        f"?{build_sql_server_query(DB_DRIVER)}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
