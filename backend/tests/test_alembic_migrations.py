"""Alembic migration tests."""

import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command


def test_alembic_upgrade_head_creates_initial_schema(tmp_path) -> None:
    """The migration chain should build a fresh async SQLite database."""
    backend_root = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "alembic.db"

    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.attributes["database_url"] = f"sqlite+aiosqlite:///{database_path}"

    command.upgrade(config, "head")

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("select name from sqlite_master where type = 'table'")
        }
        revision = connection.execute("select version_num from alembic_version").fetchone()[0]

    assert {
        "acme_challenges",
        "alembic_version",
        "certificate_files",
        "certificate_orders",
        "deployment_targets",
    }.issubset(tables)
    assert revision == "c424a6ae6258"
