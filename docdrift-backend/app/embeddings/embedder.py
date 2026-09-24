"""Embedding generation module using OpenAI text-embedding-3-small via LangChain."""

import hashlib
import math
import os
import re
from typing import List, Optional, Union
from dotenv import load_dotenv

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.models.chunk import DocumentChunk

# Load environment variables from .env if present
load_dotenv()


class DeterministicTestEmbeddings(Embeddings):
    """Deterministic 1536-dimensional embedding generator for offline testing and CI.

    Used when OPENAI_API_KEY is not configured or in offline environments.
    Uses token-hashed feature projection normalized to unit Euclidean length to produce
    valid cosine similarities for semantic search and filter verification.
    """

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vector

        for word in words:
            # Deterministic hash mapped across the 1536 dimensions
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


def get_embedding_model(api_key: Optional[str] = None) -> Embeddings:
    """Initializes and returns the LangChain embedding model.

    Attempts to use OpenAI text-embedding-3-small if a valid OPENAI_API_KEY is set.
    If the key is missing or set to placeholder text, seamlessly falls back to
    DeterministicTestEmbeddings (1536 dims) to enable offline execution and testing.

    Args:
        api_key: Optional explicit OpenAI API key override.

    Returns:
        Embeddings instance configured for the application.
    """
    key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
    placeholder_keys = {"", "your_key_here", "your_openai_api_key_here", "none"}

    if key and key.lower() not in placeholder_keys:
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=key,
            max_retries=2,
        )

    print("[INFO] OPENAI_API_KEY not configured or placeholder. Using 1536-dim deterministic test embedder.")
    return DeterministicTestEmbeddings(dimension=1536)


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
