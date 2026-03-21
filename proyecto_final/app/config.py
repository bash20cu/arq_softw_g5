import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


class Config:
    SECRET_KEY = _require_env("SECRET_KEY")
    DB_HOST = _require_env("MSSQL_HOST")
    DB_PORT = _require_env("MSSQL_PORT")
    DB_NAME = _require_env("MSSQL_DB")
    DB_USER = _require_env("MSSQL_USER")
    DB_PASSWORD = _require_env("MSSQL_PASSWORD")
    DB_DRIVER = _require_env("MSSQL_DRIVER")

    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://"
        f"{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@"
        f"{DB_HOST}:{DB_PORT}/{quote_plus(DB_NAME)}"
        f"?driver={quote_plus(DB_DRIVER)}&TrustServerCertificate=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
