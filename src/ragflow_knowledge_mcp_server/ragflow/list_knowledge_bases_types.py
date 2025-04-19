"""list_knowledge_bases_types.py: This file contains the function to get the list of knowledge types."""

"""Example result JSON:
{
    "code": 0,
    "data": [
        {
            "avatar": "",
            "chunk_count": 59,
            "create_date": "Sat, 14 Sep 2024 01:12:37 GMT",
            "create_time": 1726276357324,
            "created_by": "69736c5e723611efb51b0242ac120007",
            "description": null,
            "document_count": 1,
            "embedding_model": "BAAI/bge-large-zh-v1.5",
            "id": "6e211ee0723611efa10a0242ac120007",
            "language": "English",
            "name": "mysql",
            "chunk_method": "knowledge_graph",
            "parser_config": {
                "chunk_token_num": 8192,
                "delimiter": "\\n!?;。；！？",
                "entity_types": [
                    "organization",
                    "person",
                    "location",
                    "event",
                    "time"
                ]
            },
            "permission": "me",
            "similarity_threshold": 0.2,
            "status": "1",
            "tenant_id": "69736c5e723611efb51b0242ac120007",
            "token_num": 12744,
            "update_date": "Thu, 10 Oct 2024 04:07:23 GMT",
            "update_time": 1728533243536,
            "vector_similarity_weight": 0.3
        }
    ]
}
"""

from pydantic import BaseModel


class ParserConfig(BaseModel):
    """Parser configuration properties."""
    chunk_token_num: int | None = None
    delimiter: str | None = None
    entity_types: list[str] | None = None
    auto_keywords: int | None = None
    auto_questions: int | None = None
    # "graphrag": {"use_graphrag": false}
    graphrag: dict | None = None
    layout_recognize: str | None = None
    # "raptor": {"use_raptor": false }
    raptor: dict | None = None


class KnowledgeBase(BaseModel):
    """Knowledge base properties."""
    avatar: str | None = None
    chunk_count: int | None = None
    create_date: str | None = None
    create_time: int | None = None
    created_by: str | None = None
    description: str | None = None
    document_count: int | None = None
    embedding_model: str | None = None
    id: str
    language: str | None = None
    name: str | None = None
    pagerank: int | None = None
    chunk_method: str | None = None
    parser_config: ParserConfig | None = None
    permission: str | None = None
    similarity_threshold: float | None = None
    status: str | None = None
    tenant_id: str | None = None
    token_num: int | None = None
    update_date: str | None = None
    update_time: int | None = None
    vector_similarity_weight: float | None = None


class ListKnowledgeBasesResult(BaseModel):
    """List knowledge bases result properties."""
    code: int | None = None
    data: list[KnowledgeBase] | None = None
