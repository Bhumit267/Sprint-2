"""Data models and schemas for generated answers and citation metadata."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation referencing a specific section in versioned documentation.

    Attributes:
        source_doc: Name of the referenced document (e.g., 'api_reference.md').
        doc_type: Inferred type of the document (e.g., 'api_reference', 'migration_guide').
        version: Document version tag (e.g., 'v2.1', 'v3.0').
        section: Header or section title where the fact originated.
    """
    source_doc: str = Field(..., description="File name of the source document")
    doc_type: str = Field(..., description="Category of the document")
    version: str = Field(..., description="Version of the document")
    section: str = Field(..., description="Section or heading title")

    def to_dict(self) -> Dict[str, str]:
        """Convert citation to dictionary representation."""
        return self.model_dump()


class AnswerResponse(BaseModel):
    """Structured response containing the grounded answer, citations, and refusal status.

    Attributes:
        answer: Generated text response or explicit refusal statement.
        citations: List of unique citations referenced by retrieved context.
        is_refusal: True if no relevant context was found or model explicitly refused.
        version: Target version queried.
        question: Original user question.
    """
    answer: str = Field(..., description="Grounded answer text or refusal explanation")
    citations: List[Citation] = Field(default_factory=list, description="Exact source citations")
    is_refusal: bool = Field(default=False, description="Flag indicating lack of grounded information")
    version: str = Field(..., description="Target version queried")
    question: str = Field(..., description="Original user question")

    def to_dict(self) -> Dict[str, Any]:
        """Convert answer response to dictionary representation required by specifications."""
        return {
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "is_refusal": self.is_refusal,
            "version": self.version,
            "question": self.question,
        }
