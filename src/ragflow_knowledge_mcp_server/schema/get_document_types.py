"""get_document_types.py."""

from typing import Any

from pydantic import BaseModel


class Document(BaseModel):
    name: str
    metadata: dict[str, Any] | None = None


class GetDocumentsResult(BaseModel):
    documents: list[Document] | None = None
