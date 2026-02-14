"""Pydantic schemas for document-related contracts."""

from pydantic import BaseModel


class DocumentSchema(BaseModel):
    id: int | None = None
    source_file: str
    status: str
