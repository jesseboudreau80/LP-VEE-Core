"""Pydantic schemas for license-related contracts."""

from pydantic import BaseModel


class LicenseSchema(BaseModel):
    id: int | None = None
    document_id: int | None = None
    license_type: str | None = None
    status: str
