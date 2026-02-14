"""SQLite database lifecycle utilities."""

from __future__ import annotations

import sqlite3

from app.db.models import ALL_TABLES


def get_connection(db_path: str) -> sqlite3.Connection:
    """Create a SQLite connection."""

    return sqlite3.connect(db_path)


def initialize_database(db_path: str) -> None:
    """Initialize all required v1 tables."""

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        for ddl in ALL_TABLES:
            cursor.execute(ddl)
        conn.commit()
    finally:
        conn.close()
