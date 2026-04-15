"""Helpers for SQL Server ODBC driver selection."""

from __future__ import annotations

from pathlib import Path
import subprocess

from urllib.parse import quote_plus

import pyodbc


SQL_SERVER_DRIVER_FALLBACKS = (
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
    "FreeTDS",
)


def resolve_sql_driver(preferred_driver: str, *, strict: bool = False) -> str:
    """Pick an installed SQL Server-capable ODBC driver."""

    requested = preferred_driver.strip()
    installed = {driver.strip() for driver in pyodbc.drivers()}
    candidates = (requested, *SQL_SERVER_DRIVER_FALLBACKS)

    if requested in installed and _driver_library_exists(requested):
        return requested

    for driver in candidates:
        if driver in installed and _driver_library_exists(driver):
            return driver

    installed_text = ", ".join(sorted(installed)) or "none"
    broken = sorted(
        {
            driver
            for driver in candidates
            if driver in installed and not _driver_library_exists(driver)
        }
    )
    broken_text = f" Registered but unusable drivers: {', '.join(broken)}." if broken else ""
    if strict:
        raise RuntimeError(
            "No usable SQL Server ODBC driver was found. "
            f"Requested: {requested!r}. Installed drivers: {installed_text}.{broken_text} "
            "Install ODBC Driver 18 for SQL Server or set MSSQL_DRIVER to an installed "
            "SQL Server-compatible driver such as FreeTDS."
        )

    return requested


def build_sql_server_query(driver: str) -> str:
    """Build ODBC query params for SQLAlchemy's pyodbc URL."""

    query_params = [f"driver={quote_plus(driver)}"]
    if driver.startswith("ODBC Driver "):
        query_params.append("TrustServerCertificate=yes")
    return "&".join(query_params)


def _driver_library_exists(driver: str) -> bool:
    """Return False when unixODBC points a registered driver to a missing file."""

    try:
        result = subprocess.run(
            ["odbcinst", "-q", "-d", "-n", driver],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return True

    if result.returncode != 0:
        return True

    paths = _driver_paths_from_odbcinst(result.stdout)
    return not paths or any(path.exists() for path in paths)


def _driver_paths_from_odbcinst(output: str) -> list[Path]:
    paths = []
    for line in output.splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip().lower().startswith("driver"):
            paths.append(Path(value.strip()))
    return paths
