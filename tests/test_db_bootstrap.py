from pathlib import Path

from app import db_bootstrap


def test_bootstrap_creates_schema_and_seed_when_database_does_not_exist(monkeypatch):
    calls = []

    monkeypatch.setattr(db_bootstrap, "_database_exists", lambda server_uri, db_name: False)
    monkeypatch.setattr(
        db_bootstrap,
        "run_sql_file",
        lambda server_uri, sql_file, db_name=None: calls.append(Path(sql_file).name),
    )

    db_bootstrap.bootstrap_database(
        db_user="postgres",
        db_password="secret",
        db_host="localhost",
        db_port="5432",
        db_name="test_db",
    )

    assert calls == ["schema.sql", "seed.sql"]


def test_bootstrap_seeds_catalogs_when_database_exists(monkeypatch):
    calls = []

    monkeypatch.setattr(db_bootstrap, "_database_exists", lambda server_uri, db_name: True)
    monkeypatch.setattr(
        db_bootstrap,
        "_ensure_catalogs_seeded",
        lambda server_uri, db_name, catalog_seed_path: calls.append(Path(catalog_seed_path).name),
    )
    monkeypatch.setattr(
        db_bootstrap,
        "run_sql_file",
        lambda server_uri, sql_file, db_name=None: calls.append(Path(sql_file).name),
    )

    db_bootstrap.bootstrap_database(
        db_user="postgres",
        db_password="secret",
        db_host="localhost",
        db_port="5432",
        db_name="test_db",
    )

    assert calls == ["catalog_seed.sql"]
