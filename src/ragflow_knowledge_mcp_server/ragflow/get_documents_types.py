"""get_documents_types.py: Classes for RAGFlow Knowledge API get documents."""

"""Example result JSON
{
  "data": [
    {
      "id": "",
      "position": 1,
      "data_source_type": "file_upload",
      "data_source_info": null,
      "dataset_process_rule_id": null,
      "name": "ragflow",
      "created_from": "",
      "created_by": "",
      "created_at": 1681623639,
      "tokens": 0,
      "indexing_status": "waiting",
      "error": null,
      "enabled": true,
      "disabled_at": null,
      "disabled_by": null,
      "archived": false
    },
  ],
  "has_more": false,
  "limit": 20,
  "total": 9,
  "page": 1
}
"""

from typing import Any

from pydantic import BaseModel


class DocMetadataValue(BaseModel):
    id: str
    name: str
    type: str | None = None
    value: str | None = None


class Data(BaseModel):
    """Data for RAGFlow Knowledge API get documents."""
    id: str
    position: int | None = None
    data_source_type: str | None = None
    data_source_info: dict | None = None
    data_source_detail_dict: dict | None = None
    dataset_process_rule_id: str | None = None
    name: str | None = None
    created_from: str | None = None
    created_by: str | None = None
    created_at: int | None = None
    tokens: int | None = None
    indexing_status: str | None = None
    error: Any | None = None
    enabled: bool | None = True
    disabled_at: Any | None = None
    disabled_by: Any | None = None
    archived: bool | None = None
    display_status: str | None = None
    word_count: int | None = None
    hit_count: int | None = None
    doc_form: str | None = None
    doc_metadata: list[DocMetadataValue] | None = None


class GetDocumentsResult(BaseModel):
    """Result of getting documents from RAGFlow Knowledge API."""
    data: list[Data] | None = None
    has_more: bool | None = False
    limit: int | None = None
    total: int | None = None
    page: int | None = None
