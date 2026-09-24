"""End-to-end question answering pipeline connecting retrieval to grounded generation."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.generation.generator import generate_answer
from app.retrieval.search import search
from app.retrieval.vector_store import DEFAULT_COLLECTION_NAME


def answer_question(
    question: str,
    version: str,
    top_k: int = 5,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[Union[str, Path]] = None,
    embedding_model: Optional[Any] = None,
    llm_model: Optional[Any] = None,
) -> Dict[str, Any]:
    """Answers a developer question for a specific product version end-to-end.

    Pipeline:
    1. Retrieval: Performs similarity search filtered strictly by the specified version.
    2. Generation: Injects retrieved version-matched chunks into gpt-4o-mini prompt.
    3. Verification: Checks for refusal conditions and formats exact citations.

    Args:
        question: Developer's question.
        version: Required version string (e.g., 'v2.1', 'v3.0', 'v3.2').
        top_k: Number of retrieved candidate chunks.
        collection_name: Chroma collection name.
        persist_dir: Vector database persistence path.
        embedding_model: Optional custom embedding model.
        llm_model: Optional custom LLM model.

    Returns:
        Dictionary conforming to:
        {
            "answer": str,
            "citations": [
                {
                    "source_doc": str,
                    "doc_type": str,
                    "version": str,
                    "section": str
                },
                ...
            ],
            "is_refusal": bool
        }
    """
    # 1. Retrieve version-filtered candidate chunks
    retrieved_chunks = search(
        query=question,
        version=version,
        top_k=top_k,
        collection_name=collection_name,
        persist_dir=persist_dir,
        embedding_model=embedding_model,
    )

    # 2. Generate grounded answer using retrieved context
    return generate_answer(
        question=question,
        version=version,
        chunks=retrieved_chunks,
        llm_model=llm_model,
    )
