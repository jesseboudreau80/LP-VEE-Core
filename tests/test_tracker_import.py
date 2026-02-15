"""Tracker importer behavior tests."""

import pandas as pd

from app.db.database import get_connection, initialize_database
from app.services.tracker_importer import TrackerImporter


def _write_tracker(path, rows):
    dataframe = pd.DataFrame(rows)
    dataframe.to_excel(path, index=False)


def test_imports_valid_rows(tmp_path):
    db_path = tmp_path / "tracker.db"
    initialize_database(str(db_path))

    tracker_file = tmp_path / "tracker.xlsx"
    _write_tracker(
        tracker_file,
        [
            {
                "Center ID": "C-001",
                "License/Permit Type": "Health Permit",
                "Issuing Authority": "County",
                "Jurisdiction": "CA",
                "License/Permit Number": "12345",
                "Expiration Date": "2024-12-31",
                "Renewal Window Start": "2024-10-01",
                "Status": "Active",
            },
            {
                "Center ID": "C-002",
                "License/Permit Type": "Fire Permit",
                "Issuing Authority": "City",
                "Jurisdiction": "CA",
                "License/Permit Number": "67890",
                "Expiration Date": "2024-11-30",
                "Renewal Window Start": "2024-09-01",
                "Status": "Active",
            },
        ],
    )

    importer = TrackerImporter(str(db_path))
    summary = importer.import_tracker(str(tracker_file))
    assert summary == {"processed": 2, "inserted": 2, "updated": 0, "skipped": 0}

    conn = get_connection(str(db_path))
    try:
        count = conn.execute("SELECT COUNT(*) FROM tracker_entries").fetchone()[0]
        assert count == 2
    finally:
        conn.close()


def test_skips_rows_missing_required_fields(tmp_path):
    db_path = tmp_path / "tracker.db"
    initialize_database(str(db_path))

    tracker_file = tmp_path / "tracker.xlsx"
    _write_tracker(
        tracker_file,
        [
            {
                "Center ID": "C-003",
                "License/Permit Type": "Health Permit",
                "Issuing Authority": "County",
            },
            {
                "Center ID": "C-004",
                "License/Permit Type": "Fire Permit",
                "Issuing Authority": None,
                "Jurisdiction": "NV",
            },
        ],
    )

    importer = TrackerImporter(str(db_path))
    summary = importer.import_tracker(str(tracker_file))
    assert summary == {"processed": 2, "inserted": 1, "updated": 0, "skipped": 1}

    conn = get_connection(str(db_path))
    try:
        count = conn.execute("SELECT COUNT(*) FROM tracker_entries").fetchone()[0]
        assert count == 1
    finally:
        conn.close()


def test_parses_dates_to_iso_strings(tmp_path):
    db_path = tmp_path / "tracker.db"
    initialize_database(str(db_path))

    tracker_file = tmp_path / "tracker.xlsx"
    _write_tracker(
        tracker_file,
        [
            {
                "Center ID": 101,
                "License/Permit Type": "Health Permit",
                "Issuing Authority": "State",
                "Expiration Date": "3/1/2025",
                "Renewal Window Start": pd.Timestamp("2025-02-01"),
            }
        ],
    )

    importer = TrackerImporter(str(db_path))
    importer.import_tracker(str(tracker_file))

    conn = get_connection(str(db_path))
    try:
        row = conn.execute(
            """
            SELECT center_id, expiration_date, renewal_window_start
            FROM tracker_entries
            WHERE center_id = ?
            """,
            ("101",),
        ).fetchone()
        assert row == ("101", "2025-03-01", "2025-02-01")
    finally:
        conn.close()


def test_upsert_updates_existing_record(tmp_path):
    db_path = tmp_path / "tracker.db"
    initialize_database(str(db_path))

    tracker_file = tmp_path / "tracker.xlsx"
    _write_tracker(
        tracker_file,
        [
            {
                "Center ID": "C-005",
                "License/Permit Type": "Health Permit",
                "Issuing Authority": "County",
                "Status": "Active",
                "License/Permit Number": "1111",
            }
        ],
    )

    importer = TrackerImporter(str(db_path))
    importer.import_tracker(str(tracker_file))

    _write_tracker(
        tracker_file,
        [
            {
                "Center ID": "C-005",
                "License/Permit Type": "Health Permit",
                "Issuing Authority": "County",
                "Status": "Expired",
                "License/Permit Number": "2222",
            }
        ],
    )
    summary = importer.import_tracker(str(tracker_file))
    assert summary == {"processed": 1, "inserted": 0, "updated": 1, "skipped": 0}

    conn = get_connection(str(db_path))
    try:
        row = conn.execute(
            """
            SELECT status, license_number, raw
            FROM tracker_entries
            WHERE center_id = ? AND license_permit_type = ? AND issuing_authority = ?
            """,
            ("C-005", "Health Permit", "County"),
        ).fetchone()
        assert row[0] == "Expired"
        assert row[1] == "2222"
        assert '"status": "Expired"' in row[2]
        assert "Active" not in row[2]
    finally:
        conn.close()
