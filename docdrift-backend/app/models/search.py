"""Data models and schemas for vector retrieval and search results."""

from typing import Any, Dict
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Represents a retrieved document chunk with similarity ranking and metadata.

    Attributes:
        text: Matched chunk text.
        similarity_score: Calculated cosine similarity score (0.0 to 1.0).
        source_doc: Name of the source markdown document.
        doc_type: Category of the document (api_reference, migration_guide, changelog).
        version: Document version tag.
        chunk_index: Position index within original document.
        section: Section heading context.
        metadata: Full metadata dictionary for backward compatibility.
    """
    text: str = Field(..., description="Document chunk text")
    similarity_score: float = Field(..., description="Cosine similarity score (higher is closer)")
    source_doc: str = Field(..., description="Source file name")
    doc_type: str = Field(..., description="Inferred document type")
    version: str = Field(..., description="Product version string")
    chunk_index: int = Field(..., description="Chunk index within the file")
    section: str = Field(default="General", description="Markdown section heading")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw metadata dictionary")

    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary representation."""
        return self.model_dump()
