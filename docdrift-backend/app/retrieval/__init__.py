"""Vector store management, document indexing, and version-filtered retrieval."""

from app.retrieval.vector_store import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_PERSIST_DIR,
    get_chroma_client,
    get_collection,
    index_chunks,
)
from app.retrieval.search import build_chroma_filter, search

__all__ = [
    "DEFAULT_COLLECTION_NAME",
    "DEFAULT_PERSIST_DIR",
    "get_chroma_client",
    "get_collection",
    "index_chunks",
    "build_chroma_filter",
    "search",
]
