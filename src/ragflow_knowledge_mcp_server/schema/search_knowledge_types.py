"""search_knowledge_types.py: This file defines the schema for the searching knowledge tool."""

from pydantic import BaseModel


class Knowledge(BaseModel):
    """Knowledge object.

    Properties:
        - score: Relevance score of the knowledge.
        - content: The content of the knowledge.
    """
    score: float | None = None
    content: str


class SearchKnowledgeResult(BaseModel):
    """Search knowledge result.

    Properties:
        - knowledge_list     A list of knowledge objects returned by the search.
        - knowledge_base_id: The ID of the knowledge base(dataset) from which the knowledge was retrieved.
    """
    knowledge_list: list[Knowledge]
    knowledge_base_id: str | None = None

    def get_simple_text(self) -> str:
        """Get a simple text representation of the knowledge result.

        Returns:
            str: A string representation of the knowledge result.
        """
        if not self.knowledge_list:
            return "**No knowledge found.**"

        result_title = f"**Found {len(self.knowledge_list)} knowledge(s)** (base ID: {self.knowledge_base_id}):\n\n"
        result_content = "\n".join([
            f"{i + 1}. {knowledge.content}{f' (score: {knowledge.score})' if knowledge.score is not None else ''}"
            for i, knowledge in enumerate(self.knowledge_list)
        ])

        return result_title + result_content
