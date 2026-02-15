"""Tracker importer service implementation."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.db.database import get_connection


class TrackerImporter:
    """Import tracker XLSX data into the SQLite database."""

    FIELD_ALIASES = {
        "center": "center_id",
        "center_id": "center_id",
        "center_code": "center_id",
        "license_permit_type": "license_permit_type",
        "license_type": "license_permit_type",
        "license_permit": "license_permit_type",
        "issuing_authority": "issuing_authority",
        "authority": "issuing_authority",
        "agency_name": "issuing_authority",
        "jurisdiction": "jurisdiction",
        "license_number": "license_number",
        "license_permit_number": "license_number",
        "license_no": "license_number",
        "expiration_date": "expiration_date",
        "expiration": "expiration_date",
        "renewal_window_start": "renewal_window_start",
        "renewal_start": "renewal_window_start",
        "status": "status",
        "effective_date": "effective_date",
        "renewal_frequency": "renewal_frequency",
        "comments": "comments",
    }

    TRACKER_FIELDS = (
        "center_id",
        "license_permit_type",
        "issuing_authority",
        "jurisdiction",
        "license_number",
        "expiration_date",
        "renewal_window_start",
        "status",
    )

    REQUIRED_FIELDS = ("center_id", "license_permit_type", "issuing_authority")
    DATE_FIELDS = ("expiration_date", "renewal_window_start")

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def import_tracker(self, tracker_path: str) -> dict[str, int]:
        dataframe = self._load_dataframe(Path(tracker_path))
        records = self._normalize_records(dataframe)

        summary = {
            "processed": len(records),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

        conn = get_connection(self.db_path)
        try:
            for record in records:
                if not self._has_required_fields(record):
                    summary["skipped"] += 1
                    continue

                action = self._upsert_record(conn, record)
                if action == "inserted":
                    summary["inserted"] += 1
                elif action == "updated":
                    summary["updated"] += 1

            conn.commit()
        finally:
            conn.close()

        return summary

    def _load_dataframe(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"Tracker file not found: {path}")

        return pd.read_excel(path, header=4)

    def _normalize_records(self, dataframe: pd.DataFrame) -> list[dict[str, Any]]:
        renamed_cols = {col: self._map_column(col) for col in dataframe.columns}
        normalized_df = dataframe.rename(columns=renamed_cols)

        for field in self.TRACKER_FIELDS:
            if field not in normalized_df.columns:
                normalized_df[field] = None

        normalized_rows: list[dict[str, Any]] = []

        for _, row in normalized_df.iterrows():
            cleaned_row: dict[str, Any] = {}
            for column, value in row.items():
                cleaned_row[column] = self._normalize_value(column, value)
            if any(cleaned_row.get(field) is not None for field in self.REQUIRED_FIELDS):
                normalized_rows.append(cleaned_row)

        return normalized_rows

    def _map_column(self, column: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
        return self.FIELD_ALIASES.get(normalized, normalized)

    def _normalize_value(self, column: str, value: Any) -> Any:
        if pd.isna(value):
            return None

        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None

        if column in self.DATE_FIELDS:
            return self._parse_date(value)

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        if isinstance(value, (int, float)):
            return str(value)

        return value

    def _parse_date(self, value: Any) -> str | None:
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date().isoformat()

    def _has_required_fields(self, row: dict[str, Any]) -> bool:
        return all(row.get(field) is not None for field in self.REQUIRED_FIELDS)

    def _upsert_record(self, conn, row: dict[str, Any]) -> str:
        payload = {field: row.get(field) for field in self.TRACKER_FIELDS}
        raw_json = self._raw_json(row)
        now = datetime.now(UTC).isoformat()

        cursor = conn.cursor()

        existing = cursor.execute(
            """
            SELECT id FROM tracker_entries
            WHERE center_id = ? AND license_permit_type = ? AND issuing_authority = ?
            """,
            (
                payload["center_id"],
                payload["license_permit_type"],
                payload["issuing_authority"],
            ),
        ).fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE tracker_entries
                SET jurisdiction = ?,
                    license_number = ?,
                    expiration_date = ?,
                    renewal_window_start = ?,
                    status = ?,
                    raw = ?,
                    updated_at = ?
                WHERE center_id = ? AND license_permit_type = ? AND issuing_authority = ?
                """,
                (
                    payload.get("jurisdiction"),
                    payload.get("license_number"),
                    payload.get("expiration_date"),
                    payload.get("renewal_window_start"),
                    payload.get("status"),
                    raw_json,
                    now,
                    payload["center_id"],
                    payload["license_permit_type"],
                    payload["issuing_authority"],
                ),
            )
            return "updated"

        cursor.execute(
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
                payload.get("center_id"),
                payload.get("license_permit_type"),
                payload.get("issuing_authority"),
                payload.get("jurisdiction"),
                payload.get("license_number"),
                payload.get("expiration_date"),
                payload.get("renewal_window_start"),
                payload.get("status"),
                raw_json,
                now,
                now,
            ),
        )

        return "inserted"

    def _raw_json(self, row: dict[str, Any]) -> str:
        normalized = {k: v for k, v in row.items() if v is not None}
        return json.dumps(normalized, sort_keys=True, default=str)
