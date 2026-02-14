"""SQLite database lifecycle utilities."""

from __future__ import annotations

import sqlite3

from app.db.models import (
    ALL_TABLES,
    LICENSES_TABLE,
    REQUIRED_LICENSE_COLUMNS,
)


def get_connection(db_path: str) -> sqlite3.Connection:
    """Create a SQLite connection."""

    return sqlite3.connect(db_path)


def initialize_database(db_path: str) -> None:
    """Initialize all required v1 tables."""

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        for ddl in ALL_TABLES:
            if ddl is LICENSES_TABLE:
                continue
            cursor.execute(ddl)

        _ensure_licenses_schema(cursor)
        conn.commit()
    finally:
        conn.close()


def _ensure_licenses_schema(cursor: sqlite3.Cursor) -> None:
    """Ensure licenses table matches required Phase 1A schema."""

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='licenses';"
    )
    exists = cursor.fetchone() is not None

    if exists:
        cursor.execute("PRAGMA table_info(licenses);")
        existing_columns = {row[1] for row in cursor.fetchall()}
        if existing_columns != REQUIRED_LICENSE_COLUMNS:
            cursor.execute("DROP TABLE licenses;")

    cursor.execute(LICENSES_TABLE)
