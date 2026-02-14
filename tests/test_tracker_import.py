from __future__ import annotations

import sqlite3

import pandas as pd

from app.db.database import initialize_database
from app.services import tracker_importer


def _write_tracker(path, rows):
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)


def _fetch_licenses(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            """
            SELECT center_id, license_permit_type, issuing_authority,
                   jurisdiction, license_number, expiration_date,
                   renewal_window_start, status
            FROM licenses
            ORDER BY id
            """
        )
        return cur.fetchall()
    finally:
        conn.close()


def test_import_valid_rows(tmp_path, monkeypatch):
    db_path = tmp_path / "vee.db"
    tracker_path = tmp_path / "tracker.xlsx"

    _write_tracker(
        tracker_path,
        [
            {
                "Center ID": "1001",
                "License Permit Type": "Food License",
                "Issuing Authority": "City Health",
                "Jurisdiction": "CA",
                "License Number": "ABC-123",
                "Expiration Date": "2026-01-10",
                "Renewal Window Start": "2025-12-01",
                "Status": "Active",
            }
        ],
    )

    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.9")
    monkeypatch.setenv("INBOX_PATH", str(tmp_path / "inbox"))
    monkeypatch.setenv("OUTBOX_PATH", str(tmp_path / "outbox"))
    monkeypatch.setenv("TRACKER_PATH", str(tmp_path))
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    initialize_database(str(db_path))
    result = tracker_importer.import_tracker(str(tracker_path))

    assert result == {"imported": 1, "updated": 0, "skipped": 0}
    rows = _fetch_licenses(str(db_path))
    assert rows[0][0] == "1001"
    assert rows[0][5] == "2026-01-10"


def test_skip_missing_required_fields(tmp_path, monkeypatch):
    db_path = tmp_path / "vee.db"
    tracker_path = tmp_path / "tracker_missing.xlsx"

    _write_tracker(
        tracker_path,
        [
            {
                "Center": "1001",
                "License Type": "Food License",
                "Issuing Authority": "City Health",
                "Jurisdiction": "CA",
                "Expiration Date": "2026-01-10",
            },
            {
                "Center ID": "1002",
                "License Permit Type": "",
                "Issuing Authority": "City Health",
                "Jurisdiction": "CA",
                "Expiration Date": "2026-01-10",
            },
        ],
    )

    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.9")
    monkeypatch.setenv("INBOX_PATH", str(tmp_path / "inbox"))
    monkeypatch.setenv("OUTBOX_PATH", str(tmp_path / "outbox"))
    monkeypatch.setenv("TRACKER_PATH", str(tmp_path))
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    initialize_database(str(db_path))
    result = tracker_importer.import_tracker(str(tracker_path))

    assert result == {"imported": 1, "updated": 0, "skipped": 1}


def test_date_parsing(tmp_path, monkeypatch):
    db_path = tmp_path / "vee.db"
    tracker_path = tmp_path / "tracker_dates.xlsx"

    _write_tracker(
        tracker_path,
        [
            {
                "Center ID": "1001",
                "License Permit Type": "Fire Permit",
                "Issuing Authority": "Fire Dept",
                "Jurisdiction": "TX",
                "Expiration Date": "03/15/2027",
                "Renewal Start": "2027/02/15",
            }
        ],
    )

    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.9")
    monkeypatch.setenv("INBOX_PATH", str(tmp_path / "inbox"))
    monkeypatch.setenv("OUTBOX_PATH", str(tmp_path / "outbox"))
    monkeypatch.setenv("TRACKER_PATH", str(tmp_path))
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    initialize_database(str(db_path))
    result = tracker_importer.import_tracker(str(tracker_path))

    assert result == {"imported": 1, "updated": 0, "skipped": 0}
    rows = _fetch_licenses(str(db_path))
    assert rows[0][5] == "2027-03-15"
    assert rows[0][6] == "2027-02-15"


def test_upsert_behavior(tmp_path, monkeypatch):
    db_path = tmp_path / "vee.db"
    tracker_path = tmp_path / "tracker_upsert.xlsx"

    _write_tracker(
        tracker_path,
        [
            {
                "Center ID": "1001",
                "License Permit Type": "Food License",
                "Issuing Authority": "City Health",
                "Jurisdiction": "CA",
                "Expiration Date": "2026-01-10",
                "Status": "Active",
            }
        ],
    )

    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.9")
    monkeypatch.setenv("INBOX_PATH", str(tmp_path / "inbox"))
    monkeypatch.setenv("OUTBOX_PATH", str(tmp_path / "outbox"))
    monkeypatch.setenv("TRACKER_PATH", str(tmp_path))
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    initialize_database(str(db_path))
    first = tracker_importer.import_tracker(str(tracker_path))
    assert first == {"imported": 1, "updated": 0, "skipped": 0}

    _write_tracker(
        tracker_path,
        [
            {
                "Center ID": "1001",
                "License Permit Type": "Food License",
                "Issuing Authority": "City Health",
                "Jurisdiction": "CA",
                "Expiration Date": "2026-06-10",
                "Status": "Renewal Pending",
            }
        ],
    )

    second = tracker_importer.import_tracker(str(tracker_path))
    assert second == {"imported": 0, "updated": 1, "skipped": 0}

    rows = _fetch_licenses(str(db_path))
    assert len(rows) == 1
    assert rows[0][5] == "2026-06-10"
    assert rows[0][7] == "Renewal Pending"
