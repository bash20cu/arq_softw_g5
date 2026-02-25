import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-cambiar-en-produccion")
    DB_USER = os.getenv("MYSQL_USER", "root")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "migue123!")
    DB_HOST = os.getenv("MYSQL_HOST", "localhost")
    DB_PORT = os.getenv("MYSQL_PORT", "3306")
    DB_NAME = os.getenv("MYSQL_DATABASE", "sistema_ventas")

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        f"{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AUTO_DB_SCHEMA_ON_START = (
        os.getenv("AUTO_DB_SCHEMA_ON_START", "false").strip().lower() == "true"
    )
    AUTO_DB_SEED_ON_START = (
        os.getenv("AUTO_DB_SEED_ON_START", "false").strip().lower() == "true"
    )
