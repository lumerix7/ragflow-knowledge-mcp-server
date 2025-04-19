"""retrieve_chunks_types.py: Classes for RAGFlow Knowledge API retrieve chunks."""

"""Example result JSON
{
    "code": 0,
    "data": {
        "chunks": [
            {
                "content": "ragflow content",
                "content_ltks": "ragflow content",
                "document_id": "5c5999ec7be811ef9cab0242ac120005",
                "document_keyword": "1.txt",
                "highlight": "<em>ragflow</em> content",
                "id": "d78435d142bd5cf6704da62c778795c5",
                "image_id": "",
                "important_keywords": [
                    ""
                ],
                "kb_id": "c7ee74067a2c11efb21c0242ac120006",
                "positions": [
                    ""
                ],
                "similarity": 0.9669436601210759,
                "term_similarity": 1.0,
                "vector_similarity": 0.8898122004035864
            }
        ],
        "doc_aggs": [
            {
                "count": 1,
                "doc_id": "5c5999ec7be811ef9cab0242ac120005",
                "doc_name": "1.txt"
            }
        ],
        "total": 1
    }
}
"""

from pydantic import BaseModel


class Chunk(BaseModel):
    """Chunk information containing content and metadata."""
    id: str
    content: str | None = None
    dataset_id: str | None = None
    document_id: str | None = None
    document_keyword: str | None = None
    highlight: str | None = None
    image_id: str | None = None
    important_keywords: list[str] | None = None
    positions: list[str] | None = None
    # 相似度
    similarity: float | None = None
    # 关键词相似度
    term_similarity: float | None = None
    # 向量相似度
    vector_similarity: float | None = None


class DocAgg(BaseModel):
    """Document aggregation information."""
    count: int | None = None
    doc_id: str | None = None
    doc_name: str | None = None


class Data(BaseModel):
    chunks: list[Chunk] | None = None
    doc_aggs: list[DocAgg] | None = None
    total: int | None = None


class RetrieveChunksResult(BaseModel):
    """Result of retrieving chunks from RAGFlow Knowledge API."""
    code: int | None = None
    data: Data | None = None
