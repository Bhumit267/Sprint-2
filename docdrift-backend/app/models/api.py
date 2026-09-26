"""API request and response schemas for FastAPI endpoints."""

from typing import List
from pydantic import BaseModel, Field
from app.models.answer import Citation


class AskRequest(BaseModel):
    """Payload for question answering endpoint.

    Attributes:
        question: Developer query text.
        version: Target documentation version (e.g. 'v2.1', 'v3.0').
    """
    question: str = Field(..., min_length=1, description="Developer query text", example="How do I get a user address?")
    version: str = Field(..., min_length=1, description="Target product version", example="v2.1")


class AskResponse(BaseModel):
    """Response payload for question answering endpoint.

    Attributes:
        answer: Generated answer text or explicit refusal message.
        citations: Traceable source citations.
        is_refusal: True if no grounded documentation was found.
    """
    answer: str = Field(..., description="Grounded answer text")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    is_refusal: bool = Field(..., description="Refusal status flag")


class IngestedDocumentInfo(BaseModel):
    """Metadata describing an ingested document.

    Attributes:
        source_doc: File name of the source markdown document.
        doc_type: Inferred category (api_reference, migration_guide, changelog).
        version: Associated product version.
    """
    id: str = Field(..., description="Document database ID")
    source_doc: str = Field(..., description="Document file name")
    doc_type: str = Field(..., description="Document category")
    version: str = Field(..., description="Product version")
    last_updated: str = Field(..., description="Last updated timestamp")


class IngestResponse(BaseModel):
    """Response returned upon completing document re-indexing.

    Attributes:
        status: Operation status string ('success').
        documents_processed: Number of raw markdown files loaded.
        indexed_chunks: Number of chunks upserted into Chroma.
    """
    status: str = Field(default="success", description="Status of ingestion")
    documents_processed: int = Field(..., description="Count of raw files parsed")
    indexed_chunks: int = Field(..., description="Count of chunks indexed in Chroma")
