"""Universal tracker importer service."""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from datetime import datetime
from typing import Any

import pandas as pd

from app.config import load_settings
from app.db.database import get_connection, initialize_database

logger = logging.getLogger(__name__)

COLUMN_ALIASES = {
    "center_id": {"center_id", "center", "store_id", "location_id", "center_number"},
    "license_permit_type": {
        "license_permit_type",
        "license_type",
        "permit_type",
        "licensepermittype",
        "license_or_permit_type",
    },
    "issuing_authority": {
        "issuing_authority",
        "authority",
        "issuer",
        "issuing_agency",
    },
    "jurisdiction": {"jurisdiction", "state", "city", "county", "region"},
    "license_number": {"license_number", "permit_number", "license_no", "number"},
    "expiration_date": {"expiration_date", "expiration", "expiry_date", "expires_on"},
    "renewal_window_start": {
        "renewal_window_start",
        "renewal_start",
        "renewal_window",
        "renewal_date",
    },
    "status": {"status", "license_status", "permit_status"},
}

REQUIRED_FIELDS = {
    "center_id",
    "license_permit_type",
    "issuing_authority",
    "jurisdiction",
    "expiration_date",
}


def import_tracker(tracker_path: str) -> dict:
    """Import tracker records from XLSX and upsert license entries."""

    settings = load_settings()
    initialize_database(settings.db_path)

    frame = pd.read_excel(tracker_path)
    frame.columns = [_to_snake_case(col) for col in frame.columns]
    mapped = _map_columns(frame)

    conn = get_connection(settings.db_path)
    try:
        imported = 0
        updated = 0
        skipped = 0

        for _, row in mapped.iterrows():
            parsed = _parse_row(row)
            if parsed is None:
                skipped += 1
                continue

            exists = _record_exists(conn, parsed)
            _upsert_license(conn, parsed)

            if exists:
                updated += 1
            else:
                imported += 1

        conn.commit()
        result = {"imported": imported, "updated": updated, "skipped": skipped}
        logger.info("Tracker import summary: %s", result)
        return result
    finally:
        conn.close()


def _to_snake_case(name: Any) -> str:
    value = str(name).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def _map_columns(frame: pd.DataFrame) -> pd.DataFrame:
    original_columns = set(frame.columns)
    renamed: dict[str, str] = {}

    for target, aliases in COLUMN_ALIASES.items():
        for col in original_columns:
            if col == target or col in aliases:
                renamed[col] = target
                break

    return frame.rename(columns=renamed)


def _parse_row(row: pd.Series) -> dict[str, Any] | None:
    normalized = {k: _clean_value(v) for k, v in row.to_dict().items()}

    for field in REQUIRED_FIELDS:
        if not normalized.get(field):
            logger.warning("Skipping row missing required field '%s': %s", field, normalized)
            return None

    expiration_date = _parse_date(normalized.get("expiration_date"))
    if expiration_date is None:
        logger.warning("Skipping row with invalid expiration_date: %s", normalized)
        return None

    renewal_window_start = _parse_date(normalized.get("renewal_window_start"))

    parsed = {
        "center_id": str(normalized["center_id"]),
        "license_permit_type": str(normalized["license_permit_type"]),
        "issuing_authority": str(normalized["issuing_authority"]),
        "jurisdiction": str(normalized["jurisdiction"]),
        "license_number": _optional_string(normalized.get("license_number")),
        "expiration_date": expiration_date,
        "renewal_window_start": renewal_window_start,
        "status": _optional_string(normalized.get("status")),
        "raw": json.dumps(normalized, default=str),
    }
    return parsed


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _parse_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if hasattr(value, "date"):
        try:
            return value.date().isoformat()
        except Exception:
            pass

    text = str(value).strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue

    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _record_exists(conn: sqlite3.Connection, payload: dict[str, Any]) -> bool:
    cursor = conn.execute(
        """
        SELECT 1
        FROM licenses
        WHERE center_id = ?
          AND license_permit_type = ?
          AND issuing_authority = ?
        LIMIT 1
        """,
        (
            payload["center_id"],
            payload["license_permit_type"],
            payload["issuing_authority"],
        ),
    )
    return cursor.fetchone() is not None


def _upsert_license(conn: sqlite3.Connection, payload: dict[str, Any]) -> None:
    now = datetime.utcnow().isoformat(timespec="seconds")

    conn.execute(
        """
        INSERT INTO licenses (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(center_id, license_permit_type, issuing_authority)
        DO UPDATE SET
            jurisdiction = excluded.jurisdiction,
            license_number = excluded.license_number,
            expiration_date = excluded.expiration_date,
            renewal_window_start = excluded.renewal_window_start,
            status = excluded.status,
            raw = excluded.raw,
            updated_at = excluded.updated_at
        """,
        (
            payload["center_id"],
            payload["license_permit_type"],
            payload["issuing_authority"],
            payload["jurisdiction"],
            payload["license_number"],
            payload["expiration_date"],
            payload["renewal_window_start"],
            payload["status"],
            payload["raw"],
            now,
            now,
        ),
    )
