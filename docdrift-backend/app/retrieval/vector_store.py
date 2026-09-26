"""Persistent Chroma vector store management and document chunk indexing."""

import os
from pathlib import Path
from typing import List, Optional, Union

from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document as LCDocument
from sqlalchemy import create_engine

from dotenv import load_dotenv

from app.config import (
    DATABASE_URL,
    DEFAULT_COLLECTION_NAME,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
)
from app.embeddings.embedder import generate_embeddings, get_embedding_model
from app.models.chunk import DocumentChunk

load_dotenv()

def get_pgvector_store(embedding_model, collection_name: str = DEFAULT_COLLECTION_NAME) -> PGVector:
    """Initializes and returns a PGVector store using Supabase."""
    return PGVector(
        embeddings=embedding_model,
        collection_name=collection_name,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

def index_chunks(
    chunks: List[DocumentChunk],
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[Union[str, Path]] = None,
    embedding_model=None,
) -> int:
    """Indexes document chunks into Supabase PGVector.
    
    Args:
        chunks: List of DocumentChunk instances to index.
        collection_name: Target collection name.
        persist_dir: Ignored (kept for backwards compatibility).
        embedding_model: Embeddings model.
        
    Returns:
        The total number of chunks indexed.
    """
    if not chunks:
        return 0

    if embedding_model is None:
        embedding_model = get_embedding_model()

    vectorstore = get_pgvector_store(embedding_model, collection_name)

    documents = []
    ids = []
    for chunk in chunks:
        doc_stem = Path(chunk.source_doc).stem
        chunk_id = f"{chunk.version}_{doc_stem}_{chunk.chunk_index}"
        
        doc = LCDocument(
            page_content=chunk.text,
            metadata=chunk.get_metadata()
        )
        documents.append(doc)
        ids.append(chunk_id)

    vectorstore.add_documents(documents, ids=ids)
    return len(chunks)
