"""schema/KnowledgeBase.py."""

from pydantic import BaseModel


class KnowledgeBase(BaseModel):
    """Knowledge base (info) properties."""

    knowledge_base_id: str
    name: str
    description: str | None = None
    provider: str | None = None
    permission: str | None = None
    indexing_technique: str | None = None
    document_count: int | None = None
    word_count: int | None = None
    created_by: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
