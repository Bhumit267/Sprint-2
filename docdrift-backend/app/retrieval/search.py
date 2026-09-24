"""Similarity search module with metadata filtering and score normalization."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.embeddings.embedder import embed_query
from app.models.search import SearchResult
from app.retrieval.vector_store import (
    DEFAULT_COLLECTION_NAME,
    get_chroma_client,
    get_collection,
)


def build_chroma_filter(
    version: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Builds a Chroma-compatible 'where' filter dictionary.

    Handles single-condition filters or multi-condition '$and' conjunctions.

    Args:
        version: Target version filter (e.g. 'v2.1', 'v3.0').
        doc_type: Target doc_type filter ('api_reference', 'migration_guide', 'changelog').

    Returns:
        Chroma where filter dictionary, or None if no filters specified.
    """
    conditions: List[Dict[str, Any]] = []

    if version:
        conditions.append({"version": {"$eq": version}})
    if doc_type:
        conditions.append({"doc_type": {"$eq": doc_type}})

    if not conditions:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}


def search(
    query: str,
    version: Optional[str] = None,
    doc_type: Optional[str] = None,
    top_k: int = 5,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[Union[str, Path]] = None,
    embedding_model=None,
) -> List[SearchResult]:
    """Searches the Chroma vector store with optional version and document type filtering.

    Pipeline:
    1. Embeds the query text using OpenAI text-embedding-3-small via LangChain.
    2. Constructs metadata filter expressions based on provided version/doc_type.
    3. Runs vector similarity search against the Chroma collection.
    4. Computes similarity scores from cosine distances.
    5. Returns typed SearchResult instances carrying all chunk metadata.

    Args:
        query: User input query text.
        version: Optional version to restrict search to (e.g., 'v2.1', 'v3.0').
        doc_type: Optional document type filter.
        top_k: Number of highest-ranking results to return.
        collection_name: Name of Chroma collection to query.
        persist_dir: Optional storage directory path.
        embedding_model: Optional Embeddings model override.

    Returns:
        List of SearchResult objects sorted by similarity score descending.
    """
    if not query.strip():
        return []

    client = get_chroma_client(persist_dir=persist_dir)
    collection = get_collection(client=client, collection_name=collection_name)

    total_count = collection.count()
    if total_count == 0:
        return []

    # 1. Embed query
    query_vector = embed_query(query, embedding_model=embedding_model)

    # 2. Build filter expression
    where_filter = build_chroma_filter(version=version, doc_type=doc_type)

    # Clamp top_k to existing collection count
    n_results = min(top_k, total_count)

    # 3. Query Chroma
    raw_results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    documents = raw_results.get("documents", [[]])[0]
    metadatas = raw_results.get("metadatas", [[]])[0]
    distances = raw_results.get("distances", [[]])[0]

    search_results: List[SearchResult] = []
    for doc_text, meta, dist in zip(documents, metadatas, distances):
        # Convert cosine distance to cosine similarity: score = 1.0 - distance
        similarity = max(0.0, round(1.0 - float(dist), 4))

        result = SearchResult(
            text=doc_text,
            similarity_score=similarity,
            source_doc=meta.get("source_doc", "unknown"),
            doc_type=meta.get("doc_type", "unknown"),
            version=meta.get("version", "unknown"),
            chunk_index=int(meta.get("chunk_index", 0)),
            section=meta.get("section", "General"),
            metadata=meta,
        )
        search_results.append(result)

    # Sort descending by similarity score
    search_results.sort(key=lambda r: r.similarity_score, reverse=True)
    return search_results
