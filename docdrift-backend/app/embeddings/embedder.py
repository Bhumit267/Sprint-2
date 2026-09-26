"""Embedding generation module using Ollama Cloud (nomic-embed-text) via LangChain."""

import hashlib
import math
import os
import re
from typing import List, Optional, Union
from dotenv import load_dotenv

from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from app.config import (
    DEFAULT_EMBEDDING_DIMENSION,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    OLLAMA_API_KEY,
    OLLAMA_BASE_URL,
)
from app.models.chunk import DocumentChunk

load_dotenv()


class DeterministicTestEmbeddings(Embeddings):
    """Deterministic 768-dimensional embedding generator for offline testing and CI.

    Used when OLLAMA_API_KEY is not configured or in offline environments.
    Uses token-hashed feature projection normalized to unit Euclidean length to produce
    valid cosine similarities for semantic search and filter verification.
    """

    def __init__(self, dimension: int = DEFAULT_EMBEDDING_DIMENSION):
        self.dimension = dimension

    def _embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vector

        for word in words:
            # Deterministic hash mapped across the embedding dimensions
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if ((h >> 16) % 2 == 0) else -1.0
            vector[idx] += sign

        # Normalize to unit length for valid cosine distance calculations
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)


class SafeOllamaEmbeddings(Embeddings):
    """Wrapper around OllamaEmbeddings that falls back gracefully if the endpoint lacks embed support."""

    def __init__(self, ollama_emb: OllamaEmbeddings, fallback: Embeddings):
        self.ollama_emb = ollama_emb
        self.fallback = fallback
        self._use_fallback = False

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._use_fallback:
            return self.fallback.embed_documents(texts)
        try:
            return self.ollama_emb.embed_documents(texts)
        except Exception as e:
            print(f"[INFO] Ollama Cloud embedding endpoint returned ({e}). Falling back to local 768-dim deterministic embeddings.")
            self._use_fallback = True
            return self.fallback.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        if self._use_fallback:
            return self.fallback.embed_query(text)
        try:
            return self.ollama_emb.embed_query(text)
        except Exception as e:
            print(f"[INFO] Ollama Cloud embedding endpoint returned ({e}). Falling back to local 768-dim deterministic embeddings.")
            self._use_fallback = True
            return self.fallback.embed_query(text)


def get_embedding_model(api_key: Optional[str] = None) -> Embeddings:
    """Initializes and returns the LangChain OllamaEmbeddings model.

    Connects to Ollama Cloud with the configured EMBEDDING_MODEL (nomic-embed-text)
    if OLLAMA_API_KEY is provided. Falls back to DeterministicTestEmbeddings (768 dims)
    if the cloud embedding endpoint is unsupported or offline.

    Args:
        api_key: Optional explicit Ollama API key override.

    Returns:
        Embeddings instance configured for the application.
    """
    key = api_key or OLLAMA_API_KEY
    placeholder_keys = {"", "your_key_here", "your_ollama_api_key_here", "none"}
    fallback = DeterministicTestEmbeddings(dimension=EMBEDDING_DIMENSION)

    if key and key.lower() not in placeholder_keys:
        headers = {"Authorization": f"Bearer {key}"}
        ollama_emb = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
            client_kwargs={"headers": headers},
            validate_model_on_init=False,
        )
        return SafeOllamaEmbeddings(ollama_emb=ollama_emb, fallback=fallback)

    return fallback


def generate_embeddings(
    chunks: List[DocumentChunk],
    embedding_model: Optional[Embeddings] = None,
) -> List[List[float]]:
    """Generates embedding vectors for a list of document chunks.

    Args:
        chunks: List of DocumentChunk instances.
        embedding_model: Optional custom Embeddings instance. If None, uses default.

    Returns:
        List of embedding vectors (one float list per chunk).
    """
    if not chunks:
        return []

    model = embedding_model or get_embedding_model()
    texts = [chunk.text for chunk in chunks]
    return model.embed_documents(texts)


def embed_query(
    query: str,
    embedding_model: Optional[Embeddings] = None,
) -> List[float]:
    """Generates an embedding vector for a single search query string.

    Args:
        query: User input query.
        embedding_model: Optional custom Embeddings instance. If None, uses default.

    Returns:
        Embedding vector as a list of floats.
    """
    model = embedding_model or get_embedding_model()
    return model.embed_query(query)
