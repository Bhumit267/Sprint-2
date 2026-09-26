"""FastAPI application entrypoint for DocDrift version-aware documentation RAG system using Ollama Cloud."""

import os
from pathlib import Path
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import (
    CHROMA_PERSIST_DIR,
    DEFAULT_COLLECTION_NAME,
    GENERATION_MODEL,
    OLLAMA_API_KEY,
    OLLAMA_BASE_URL,
    RAW_DOCS_DIR,
)
from app.generation.service import answer_question
from app.ingestion.chunker import chunk_documents
from app.ingestion.loader import load_markdown_documents
from app.models.api import AskRequest, AskResponse, IngestResponse, IngestedDocumentInfo
from app.models.chunk import RawDocument
from app.retrieval.vector_store import (
    index_chunks,
)
from app.models.db import init_db, get_db, Document
from sqlalchemy.orm import Session
from app.auth import auth_router
from app.auth.dependencies import require_role
from app.supabase_client import get_supabase

load_dotenv()


def validate_environment() -> None:
    """Validates required environment configuration on server startup.

    Exits immediately with a clear red error message if OLLAMA_API_KEY is missing,
    empty, or set to placeholder text.
    """
    if os.getenv("DOCDRIFT_TEST_MODE", "").lower() == "true":
        return

    api_key = os.getenv("OLLAMA_API_KEY", "").strip()
    placeholder_keys = {"", "your_key_here", "your_ollama_api_key_here", "none"}

    if not api_key or api_key.lower() in placeholder_keys:
        red_banner = (
            "\n\033[91m"
            "================================================================================\n"
            "  CRITICAL STARTUP ERROR: OLLAMA_API_KEY is missing or empty!\n"
            "================================================================================\n"
            "  The DocDrift server requires a valid Ollama Cloud API key to run.\n"
            "  1. Obtain your key from: https://ollama.com/settings/keys\n"
            "  2. Open the file: docdrift-backend/.env\n"
            "  3. Set your key:\n"
            "       OLLAMA_API_KEY=your_actual_ollama_key_here\n"
            "  4. Save the file and restart the server.\n"
            "================================================================================\033[0m\n"
        )
        sys.stderr.write(red_banner)
        sys.stderr.flush()
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager running startup checks before handling requests."""
    validate_environment()
    init_db()
    yield


app = FastAPI(
    title="DocDrift Backend (Ollama Cloud)",
    description="Version-aware documentation Retrieval-Augmented Generation API powered by Ollama Cloud (Team: GroundTruth)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware allowing requests from Next.js frontend
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

# Mount authentication router
app.include_router(auth_router)


@app.get("/", tags=["Health"])
def root() -> Dict[str, str]:
    """Root status endpoint."""
    return {
        "status": "ok",
        "app": "DocDrift",
        "version": "1.0.0",
        "provider": "Ollama Cloud",
        "generation_model": GENERATION_MODEL,
    }


@app.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    tags=["Query"],
    summary="Query documentation with strict version isolation",
)
def ask_endpoint(
    payload: AskRequest,
    current_user: Dict[str, Any] = Depends(require_role("admin", "employee")),
) -> Dict[str, Any]:
    """Answers a developer question for a specified product version.

    Pipeline:
    1. Validates input request.
    2. Runs vector search filtered to the given version.
    3. Synthesizes a grounded answer via Ollama Cloud (llama3.2) or returns a refusal if not documented.
    4. Attaches exact citations with source_doc, doc_type, version, section.

    Raises:
        HTTPException (500): If Ollama Cloud API key is missing or authentication fails.
    """
    try:
        result = answer_question(
            question=payload.question,
            version=payload.version,
            org_id=current_user["org_id"],
            top_k=5,
            persist_dir=CHROMA_PERSIST_DIR,
        )
        return result
    except Exception as e:
        err_msg = str(e)
        if "api_key" in err_msg.lower() or "unauthorized" in err_msg.lower() or "401" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ollama Cloud authentication error: {err_msg}. Please check your OLLAMA_API_KEY in .env.",
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
def list_documents_endpoint(
    current_user: Dict[str, Any] = Depends(require_role("admin", "employee")),
    db: Session = Depends(get_db),
) -> List[Dict[str, str]]:
    """Returns all ingested documentation files tracked in Postgres."""
    try:
        org_id = current_user["org_id"]
        docs = db.query(Document).filter(Document.org_id == org_id).order_by(Document.version.desc(), Document.filename).all()
        
        return [
            {
                "id": doc.id,
                "source_doc": doc.filename,
                "doc_type": doc.doc_type,
                "version": doc.version,
                "last_updated": doc.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for doc in docs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch indexed documents from vector store: {str(e)}",
        )


@app.get(
    "/versions",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="List all distinct versions present in the organization's indexed documents",
)
def list_versions_endpoint(
    current_user: Dict[str, Any] = Depends(require_role("admin", "employee")),
    db: Session = Depends(get_db),
) -> List[str]:
    """Returns a list of unique versions available for the user's organization."""
    try:
        org_id = current_user["org_id"]
        # Query distinct versions from the Document table
        versions = db.query(Document.version).filter(Document.org_id == org_id).distinct().all()
        # Flatten the list of tuples and sort descending
        version_list = sorted([v[0] for v in versions if v[0]], reverse=True)
        return version_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch versions from database: {str(e)}",
        )

import random
from app.generation.generator import get_llm

@app.get(
    "/suggestions",
    response_model=List[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    tags=["Query"],
    summary="Dynamically generate suggested questions based on the organization's documents",
)
def generate_suggestions_endpoint(
    version: str = None,
    current_user: Dict[str, Any] = Depends(require_role("admin", "employee")),
) -> List[Dict[str, str]]:
    """Fetches random chunks from the org's documents and asks the LLM to generate diverse questions."""
    try:
        from app.retrieval.vector_store import get_pgvector_store
        from app.embeddings.embedder import get_embedding_model
        
        org_id = current_user["org_id"]
        
        where_clause = {"org_id": {"$eq": org_id}}
        if version:
            where_clause["version"] = {"$eq": version}

        vectorstore = get_pgvector_store(get_embedding_model())
        
        # Use similarity search with a general query to get 3 chunks
        results = vectorstore.similarity_search("documentation examples configuration", k=3, filter=where_clause)
        
        if not results:
            # Fallback if no docs
            return [
                {"text": "How do I get started?", "version": version or "v1.0"},
                {"text": "What are the authentication methods?", "version": version or "v1.0"}
            ]
            
        context_texts = [doc.page_content for doc in results]
        versions = [doc.metadata.get("version", "unknown") for doc in results]
        
        # Call LLM to generate questions
        llm = get_llm(GENERATION_MODEL)
        
        prompt = (
            "You are a developer documentation assistant. Based on the following documentation snippets, "
            "generate exactly 3 distinct, concise, and helpful questions that a developer might ask. "
            "Return ONLY the questions, one per line, with no numbering, bullets, or extra text.\n\n"
            "Snippets:\n"
            + "\n---\n".join(context_texts)
        )
        
        response = llm.complete(prompt)
        lines = [line.strip().lstrip("-*1234567890. ") for line in response.text.split("\n") if line.strip()]
        
        suggestions = []
        for i in range(min(3, len(lines))):
            suggestions.append({
                "text": lines[i],
                "version": versions[i % len(versions)]
            })
            
        # Ensure we always return at least something
        if not suggestions:
            return [{"text": "How do I configure this?", "version": version or "v1.0"}]
            
        return suggestions
        
    except Exception as e:
        # Graceful fallback in case of LLM error so the homepage doesn't crash
        return [
            {"text": "How do I authenticate?", "version": version or "v1.0"},
            {"text": "What are the rate limits?", "version": version or "v1.0"}
        ]
@app.get(
    "/documents/{doc_id}/download",
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="Get a signed URL to download a document",
)
def download_document_endpoint(
    doc_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin", "employee")),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Generates a signed URL for an uploaded document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.org_id != current_user["org_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        supabase = get_supabase()
        res = supabase.storage.from_("documents").create_signed_url(doc.storage_path, 3600)
        return {"download_url": res["signedURL"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download link: {e}")

@app.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    tags=["Ingestion"],
    summary="Trigger document loading, chunking, and indexing pipeline",
)
def trigger_ingest_endpoint(
    file: UploadFile = File(...),
    version: str = Form(...),
    doc_type: str = Form(...),
    current_user: Dict[str, Any] = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Ingests an uploaded markdown document, saves to Supabase Storage and Postgres, then chunks/indexes."""
    try:
        content = file.file.read().decode("utf-8")
        filename = file.filename
        org_id = current_user["org_id"]
        
        # 1. Save to Supabase Storage
        supabase = get_supabase()
        bucket_name = "documents"
        
        # Ensure bucket exists (or try to create it, ignoring errors if it already exists)
        try:
            supabase.storage.create_bucket(bucket_name, {"public": False})
        except Exception:
            pass # Bucket might already exist
            
        storage_path = f"org-{org_id}/{filename}"
        
        # Upload file (overwrite if exists)
        supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=content.encode("utf-8"),
            file_options={"content-type": "text/markdown", "upsert": "true"}
        )

        # 2. Save record to Postgres
        doc_record = Document(
            org_id=org_id,
            filename=filename,
            storage_path=storage_path,
            doc_type=doc_type,
            version=version
        )
        db.add(doc_record)
        db.commit()

        # 3. Create RawDocument and chunk
        raw_doc = RawDocument(
            content=content,
            source_doc=filename,
            doc_type=doc_type,
            version=version,
            file_path=storage_path,
        )

        chunks = chunk_documents([raw_doc], org_id=org_id)

        # 4. Index chunks into persistent Chroma
        indexed_count = index_chunks(chunks=chunks, persist_dir=CHROMA_PERSIST_DIR)

        return {
            "status": "success",
            "documents_processed": 1,
            "indexed_chunks": indexed_count,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion pipeline failed: {str(e)}",
        )
