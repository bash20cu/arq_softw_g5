import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class Config:
    SECRET_KEY = _require_env("SECRET_KEY")
    DB_USER = _require_env("MYSQL_USER")
    DB_PASSWORD = _require_env("MYSQL_PASSWORD")
    DB_HOST = _require_env("MYSQL_HOST")
    DB_PORT = _require_env("MYSQL_PORT")
    DB_NAME = _require_env("MYSQL_DATABASE")

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        f"{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
