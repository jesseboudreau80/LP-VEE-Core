"""VEE orchestrator and renewal evaluation engine."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from app.db.database import get_connection

STATUS_ORDER = (
    "expired",
    "in_renewal_window",
    "due_soon",
    "upcoming",
    "active",
)


def evaluate_licenses(db_path: str) -> dict[str, int]:
    """Evaluate tracker entries and update status based on expiration timelines."""

    today = date.today()
    summary = {status: 0 for status in STATUS_ORDER}

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        rows = cursor.execute(
            """
            SELECT id, expiration_date, renewal_window_start, status
            FROM tracker_entries
            """
        ).fetchall()

        for row in rows:
            entry_id, expiration_raw, renewal_raw, current_status = row
            expiration_date = _parse_date(expiration_raw)
            renewal_window_start = _parse_date(renewal_raw)
            new_status = _determine_status(today, expiration_date, renewal_window_start)

            summary[new_status] += 1

            if new_status != current_status:
                cursor.execute(
                    """
                    UPDATE tracker_entries
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_status, datetime.now(UTC).isoformat(), entry_id),
                )

        conn.commit()
    finally:
        conn.close()

    return summary


def _parse_date(value: Any):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    try:
        return datetime.fromisoformat(str(value)).date()
    except (ValueError, TypeError):
        return None


def _determine_status(today: date, expiration_date, renewal_window_start) -> str:
    if expiration_date and expiration_date < today:
        return "expired"

    if (
        renewal_window_start
        and expiration_date
        and renewal_window_start <= today < expiration_date
    ):
        return "in_renewal_window"

    if expiration_date:
        delta_days = (expiration_date - today).days
        if 0 <= delta_days <= 30:
            return "due_soon"
        if 0 <= delta_days <= 90:
            return "upcoming"

    return "active"


class VEEOrchestrator:
    def run(self) -> None:
        raise NotImplementedError
