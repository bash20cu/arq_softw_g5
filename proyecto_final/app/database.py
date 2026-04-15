"""Instancia compartida de SQLAlchemy para todo el backend."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
