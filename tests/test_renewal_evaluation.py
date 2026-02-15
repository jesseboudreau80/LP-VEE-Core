"""Renewal evaluation engine tests."""

import json
from datetime import UTC, date, datetime, timedelta

from app.db.database import get_connection, initialize_database
from app.services.vee_orchestrator import evaluate_licenses


def _insert_entry(conn, center_id, exp_date, renewal_start, status="Pending"):
    now = datetime.now(UTC).isoformat()
    raw_data = {"center_id": center_id}
    conn.execute(
        """
        INSERT INTO tracker_entries (
            center_id,
            license_permit_type,
            issuing_authority,
            jurisdiction,
            license_number,
            expiration_date,
            renewal_window_start,
            status,
            raw,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            center_id,
            "License",
            f"Authority-{center_id}",
            None,
            None,
            exp_date,
            renewal_start,
            status,
            json.dumps(raw_data),
            now,
            now,
        ),
    )


def test_evaluate_licenses_updates_status_counts(tmp_path):
    db_path = tmp_path / "tracker.db"
    initialize_database(str(db_path))
    conn = get_connection(str(db_path))
    try:
        today = date.today()
        _insert_entry(conn, "C1", (today - timedelta(days=1)).isoformat(), (today - timedelta(days=10)).isoformat())
        _insert_entry(conn, "C2", (today + timedelta(days=20)).isoformat(), (today - timedelta(days=5)).isoformat())
        _insert_entry(conn, "C3", (today + timedelta(days=10)).isoformat(), None)
        _insert_entry(conn, "C4", (today + timedelta(days=60)).isoformat(), None)
        _insert_entry(conn, "C5", (today + timedelta(days=120)).isoformat(), None)
        conn.commit()
    finally:
        conn.close()

    summary = evaluate_licenses(str(db_path))
    assert summary == {
        "expired": 1,
        "in_renewal_window": 1,
        "due_soon": 1,
        "upcoming": 1,
        "active": 1,
    }

    conn = get_connection(str(db_path))
    try:
        statuses = dict(
            conn.execute(
                """
                SELECT center_id, status FROM tracker_entries
                """
            ).fetchall()
        )
        assert statuses["C1"] == "expired"
        assert statuses["C2"] == "in_renewal_window"
        assert statuses["C3"] == "due_soon"
        assert statuses["C4"] == "upcoming"
        assert statuses["C5"] == "active"
    finally:
        conn.close()


def test_evaluate_licenses_defaults_to_active_and_updates_status(tmp_path):
    db_path = tmp_path / "tracker.db"
    initialize_database(str(db_path))
    conn = get_connection(str(db_path))
    try:
        _insert_entry(conn, "C6", None, None, status="Pending")
        conn.commit()
    finally:
        conn.close()

    summary = evaluate_licenses(str(db_path))
    assert summary["active"] == 1
    assert all(summary[key] == 0 for key in ("expired", "in_renewal_window", "due_soon", "upcoming"))

    conn = get_connection(str(db_path))
    try:
        status = conn.execute(
            """
            SELECT status FROM tracker_entries WHERE center_id = ?
            """,
            ("C6",),
        ).fetchone()[0]
        assert status == "active"
    finally:
        conn.close()
