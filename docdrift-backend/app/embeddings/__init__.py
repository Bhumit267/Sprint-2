"""Embedding generation module using Ollama Cloud (nomic-embed-text) via LangChain."""

from app.embeddings.embedder import (
    DeterministicTestEmbeddings,
    embed_query,
    generate_embeddings,
    get_embedding_model,
)

__all__ = [
    "get_embedding_model",
    "generate_embeddings",
    "embed_query",
    "DeterministicTestEmbeddings",
]
