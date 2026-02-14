"""Smoke tests for scaffold sanity."""

from app.db.database import initialize_database


def test_database_initialization(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(str(db_path))
    assert db_path.exists()
