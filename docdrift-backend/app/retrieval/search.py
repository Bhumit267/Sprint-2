"""Similarity search module with metadata filtering and score normalization for PGVector."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.embeddings.embedder import get_embedding_model
from app.models.search import SearchResult
from app.retrieval.vector_store import (
    DEFAULT_COLLECTION_NAME,
    get_pgvector_store,
)


def build_pgvector_filter(
    version: Optional[str] = None,
    doc_type: Optional[str] = None,
    org_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Builds a Langchain PGVector compatible 'where' filter dictionary."""
    conditions: List[Dict[str, Any]] = []

    if version:
        conditions.append({"version": {"$eq": version}})
    if doc_type:
        conditions.append({"doc_type": {"$eq": doc_type}})
    if org_id:
        conditions.append({"org_id": {"$eq": org_id}})

    if not conditions:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}


def search(
    query: str,
    org_id: str,
    version: Optional[str] = None,
    doc_type: Optional[str] = None,
    top_k: int = 5,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[Union[str, Path]] = None,
    embedding_model=None,
) -> List[SearchResult]:
    """Searches the PGVector store with optional version and document type filtering."""
    if not query.strip():
        return []

    if embedding_model is None:
        embedding_model = get_embedding_model()

    vectorstore = get_pgvector_store(embedding_model, collection_name=collection_name)

    where_filter = build_pgvector_filter(version=version, doc_type=doc_type, org_id=org_id)

    raw_results = vectorstore.similarity_search_with_score(
        query,
        k=top_k,
        filter=where_filter
    )

    search_results: List[SearchResult] = []
    for doc, dist in raw_results:
        # Langchain PGVector returns cosine distance by default.
        # similarity = 1.0 - distance
        similarity = max(0.0, round(1.0 - float(dist), 4))
        meta = doc.metadata

        result = SearchResult(
            text=doc.page_content,
            similarity_score=similarity,
            source_doc=meta.get("source_doc", "unknown"),
            doc_type=meta.get("doc_type", "unknown"),
            version=meta.get("version", "unknown"),
            chunk_index=int(meta.get("chunk_index", 0)),
            section=meta.get("section", "General"),
            metadata=meta,
        )
        search_results.append(result)

    search_results.sort(key=lambda r: r.similarity_score, reverse=True)
    return search_results
