"""schema/list_knowledge_bases_types.py."""

from pydantic import BaseModel

from .KnowledgeBase import KnowledgeBase as KnowledgeBase


class ListKnowledgeBasesResult(BaseModel):
    """List knowledge bases result."""
    data: list[KnowledgeBase]
