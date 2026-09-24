"""FastAPI application entrypoint for DocDrift version-aware documentation RAG system."""

import os
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai

from app.generation.service import answer_question
from app.ingestion.chunker import chunk_documents
from app.ingestion.loader import load_markdown_documents
from app.models.api import AskRequest, AskResponse, IngestResponse, IngestedDocumentInfo
from app.retrieval.vector_store import (
    DEFAULT_COLLECTION_NAME,
    get_chroma_client,
    get_collection,
    index_chunks,
)

load_dotenv()

app = FastAPI(
    title="DocDrift Backend",
    description="Version-aware documentation Retrieval-Augmented Generation API (Team: GroundTruth)",
    version="1.0.0",
)

# 4. Configure CORS middleware allowing requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = BASE_DIR / "data" / "raw_docs"
CHROMA_PERSIST_DIR = BASE_DIR / "data" / "chroma_db"


@app.get("/", tags=["Health"])
def root() -> Dict[str, str]:
    """Root status endpoint."""
    return {"status": "ok", "app": "DocDrift", "version": "1.0.0"}


@app.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    tags=["Query"],
    summary="Query documentation with strict version isolation",
)
def ask_endpoint(payload: AskRequest) -> Dict[str, Any]:
    """Answers a developer question for a specified product version.

    Pipeline:
    1. Validates input request.
    2. Runs vector search filtered to the given version.
    3. Synthesizes a grounded answer via gpt-4o-mini or returns a refusal if not documented.
    4. Attaches exact citations with source_doc, doc_type, version, section.

    Raises:
        HTTPException (500): If OpenAI API key is missing or authentication fails.
    """
    try:
        result = answer_question(
            question=payload.question,
            version=payload.version,
            top_k=5,
            persist_dir=CHROMA_PERSIST_DIR,
        )
        return result
    except (openai.AuthenticationError, openai.OpenAIError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenAI API authentication error: {str(e)}. Please check your OPENAI_API_KEY in .env.",
        )
    except Exception as e:
        # Check for unconfigured API key or other runtime errors
        err_msg = str(e)
        if "api_key" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key is missing or invalid. Please check your .env configuration.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal processing error: {err_msg}",
        )


@app.get(
    "/documents",
    response_model=List[IngestedDocumentInfo],
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="List all indexed documents with version and doc_type",
)
def list_documents_endpoint() -> List[Dict[str, str]]:
    """Returns all ingested documentation files tracked in the Chroma vector store.

    Deduplicates metadata records by source document name and version.
    """
    try:
        client = get_chroma_client(persist_dir=CHROMA_PERSIST_DIR)
        collection = get_collection(client=client, collection_name=DEFAULT_COLLECTION_NAME)

        total_count = collection.count()
        if total_count == 0:
            return []

        # Retrieve all chunk metadata from Chroma
        stored_data = collection.get(include=["metadatas"])
        metadatas = stored_data.get("metadatas", [])

        # Deduplicate records by (source_doc, version)
        seen = set()
        documents: List[Dict[str, str]] = []

        for meta in metadatas:
            if not meta:
                continue
            source_doc = meta.get("source_doc")
            version = meta.get("version")
            doc_type = meta.get("doc_type", "unknown")

            key = (source_doc, version)
            if key not in seen and source_doc and version:
                seen.add(key)
                documents.append({
                    "source_doc": source_doc,
                    "doc_type": doc_type,
                    "version": version,
                })

        # Sort for predictable output
        documents.sort(key=lambda d: (d["version"], d["source_doc"]))
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch indexed documents from vector store: {str(e)}",
        )


@app.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    tags=["Ingestion"],
    summary="Trigger document loading, chunking, and indexing pipeline",
)
def trigger_ingest_endpoint() -> Dict[str, Any]:
    """Ingests raw markdown documentation from data/raw_docs/ and indexes chunks into Chroma.

    Allows adding or updating documentation files without restarting the backend service.
    """
    try:
        if not RAW_DOCS_DIR.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Raw documentation directory not found at: {RAW_DOCS_DIR}",
            )

        # 1. Load documents
        raw_docs = load_markdown_documents(RAW_DOCS_DIR)
        if not raw_docs:
            return {
                "status": "success",
                "documents_processed": 0,
                "indexed_chunks": 0,
            }

        # 2. Chunk documents
        chunks = chunk_documents(raw_docs)

        # 3. Index chunks into persistent Chroma
        indexed_count = index_chunks(chunks=chunks, persist_dir=CHROMA_PERSIST_DIR)

        return {
            "status": "success",
            "documents_processed": len(raw_docs),
            "indexed_chunks": indexed_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion pipeline failed: {str(e)}",
        )
