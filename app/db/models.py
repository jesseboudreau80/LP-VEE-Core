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
    document_id INTEGER,
    license_type TEXT,
    jurisdiction TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id)
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

TRACKER_ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS tracker_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_id TEXT NOT NULL,
    license_permit_type TEXT NOT NULL,
    issuing_authority TEXT NOT NULL,
    jurisdiction TEXT,
    license_number TEXT,
    expiration_date TEXT,
    renewal_window_start TEXT,
    status TEXT,
    raw TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(center_id, license_permit_type, issuing_authority)
);
"""

ALL_TABLES = [
    DOCUMENTS_TABLE,
    LICENSES_TABLE,
    ESCALATIONS_TABLE,
    AUDIT_LOG_TABLE,
    TRACKER_ENTRIES_TABLE,
]
