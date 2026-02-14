"""Database schema metadata for v1 SQLite tables."""

DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

LICENSES_TABLE = """
CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_id TEXT NOT NULL,
    license_permit_type TEXT NOT NULL,
    issuing_authority TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    license_number TEXT,
    expiration_date DATE NOT NULL,
    renewal_window_start DATE,
    status TEXT,
    raw TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(center_id, license_permit_type, issuing_authority)
);
"""

ESCALATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    reason TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);
"""

AUDIT_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL
);
"""

ALL_TABLES = [DOCUMENTS_TABLE, LICENSES_TABLE, ESCALATIONS_TABLE, AUDIT_LOG_TABLE]

REQUIRED_LICENSE_COLUMNS = {
    "id",
    "center_id",
    "license_permit_type",
    "issuing_authority",
    "jurisdiction",
    "license_number",
    "expiration_date",
    "renewal_window_start",
    "status",
    "raw",
    "created_at",
    "updated_at",
}
