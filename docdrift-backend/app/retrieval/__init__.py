"""Vector store management, document indexing, and version-filtered retrieval."""

from app.retrieval.vector_store import (
    DEFAULT_COLLECTION_NAME,
    get_pgvector_store,
    index_chunks,
)
from app.retrieval.search import build_pgvector_filter, search

__all__ = [
    "DEFAULT_COLLECTION_NAME",
    "get_pgvector_store",
    "index_chunks",
    "build_pgvector_filter",
    "search",
]
