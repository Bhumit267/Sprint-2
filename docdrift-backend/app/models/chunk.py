"""Data models and schemas representing ingested document chunks and raw documents."""

from typing import Any, Dict
from pydantic import BaseModel, Field


class RawDocument(BaseModel):
    """Represents a raw document loaded from the filesystem before chunking.
    
    Attributes:
        content: Full text content of the markdown document.
        source_doc: File name of the source document (e.g., 'api_reference.md').
        doc_type: Inferred document category ('api_reference', 'migration_guide', 'changelog').
        version: Product version associated with the document directory (e.g., 'v2.1').
        file_path: Absolute or relative filesystem path to the original document.
    """
    content: str = Field(..., description="Full text content of the document")
    source_doc: str = Field(..., description="File name of the document, e.g., 'api_reference.md'")
    doc_type: str = Field(..., description="Type of document, e.g., 'api_reference', 'migration_guide', 'changelog'")
    version: str = Field(..., description="Target version extracted from folder path, e.g., 'v2.1'")
    file_path: str = Field(..., description="Filesystem path of the raw document")


class DocumentChunk(BaseModel):
    """Represents an atomic text chunk derived from a document with full metadata traceability.
    
    Attributes:
        text: Segmented text content of the chunk.
        source_doc: Original file name.
        doc_type: Categorized document type.
        version: Version tag of the documentation.
        chunk_index: Zero-indexed position of this chunk within the parent document.
        section: Header or section title extracted from markdown context.
    """
    text: str = Field(..., description="Text content of the chunk")
    source_doc: str = Field(..., description="Source document file name")
    doc_type: str = Field(..., description="Inferred document type")
    version: str = Field(..., description="Product version string")
    chunk_index: int = Field(..., description="Sequential index of the chunk in the parent document")
    section: str = Field(default="General", description="Markdown section or heading context")
    org_id: str = Field(..., description="Organization ID associated with the chunk")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize chunk to a standard dictionary format.
        
        Returns:
            Dictionary containing chunk text and all metadata attributes.
        """
        return self.model_dump()

    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata dictionary excluding raw text for vector store indexing.
        
        Returns:
            Metadata dictionary containing source_doc, doc_type, version, chunk_index, section.
        """
        return {
            "source_doc": self.source_doc,
            "doc_type": self.doc_type,
            "version": self.version,
            "chunk_index": self.chunk_index,
            "section": self.section,
            "org_id": self.org_id,
        }
