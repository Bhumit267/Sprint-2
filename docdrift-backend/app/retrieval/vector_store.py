"""Persistent Chroma vector store management and document chunk indexing."""

import os
from pathlib import Path
from typing import List, Optional, Union
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from app.embeddings.embedder import generate_embeddings, get_embedding_model
from app.models.chunk import DocumentChunk

# Resolve default persistent directory to data/chroma_db
DEFAULT_PERSIST_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"
DEFAULT_COLLECTION_NAME = "docdrift_docs"


def get_chroma_client(persist_dir: Optional[Union[str, Path]] = None) -> ClientAPI:
    """Initializes and returns a persistent Chroma vector database client.

    Args:
        persist_dir: Optional custom storage path. Defaults to data/chroma_db.

    Returns:
        chromadb.PersistentClient instance.
    """
    directory = Path(persist_dir or os.getenv("CHROMA_PERSIST_DIRECTORY") or DEFAULT_PERSIST_DIR).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(directory))


def get_collection(
    client: Optional[ClientAPI] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Collection:
    """Retrieves or creates a persistent Chroma collection configured with cosine space.

    Args:
        client: Existing Chroma client. If None, initializes client with default persist dir.
        collection_name: Name of the collection in Chroma.

    Returns:
        The requested Chroma Collection instance.
    """
    c = client or get_chroma_client()
    return c.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(
    chunks: List[DocumentChunk],
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[Union[str, Path]] = None,
    embedding_model=None,
) -> int:
    """Generates embeddings and indexes document chunks into the persistent Chroma collection.

    Stores:
    - Text content as document body
    - 1536-dimensional embeddings (OpenAI text-embedding-3-small)
    - Full metadata: {source_doc, doc_type, version, chunk_index, section}
    - Deterministic, collision-free chunk IDs

    Args:
        chunks: List of DocumentChunk instances to index.
        collection_name: Target Chroma collection name.
        persist_dir: Directory where Chroma stores vector data.
        embedding_model: Optional Embeddings model override.

    Returns:
        The total number of chunks indexed into the collection.
    """
    if not chunks:
        return 0

    client = get_chroma_client(persist_dir=persist_dir)
    collection = get_collection(client=client, collection_name=collection_name)

    # Generate embeddings via embedding module
    embeddings = generate_embeddings(chunks, embedding_model=embedding_model)

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[dict] = []

    for chunk in chunks:
        # Create deterministic ID: {version}_{doc_stem}_{chunk_index}
        doc_stem = Path(chunk.source_doc).stem
        chunk_id = f"{chunk.version}_{doc_stem}_{chunk.chunk_index}"

        ids.append(chunk_id)
        documents.append(chunk.text)
        metadatas.append(chunk.get_metadata())

    # Upsert into Chroma (updates existing or inserts new)
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return len(chunks)
