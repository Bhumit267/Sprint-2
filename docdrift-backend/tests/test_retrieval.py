"""Verification and comparison test script for DocDrift retrieval and version filtering."""

from pathlib import Path
import sys

# Ensure backend root is in Python sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.loader import load_markdown_documents
from app.ingestion.chunker import chunk_documents
from app.retrieval.vector_store import index_chunks, get_chroma_client
from app.retrieval.search import search


def format_snippet(text: str, max_length: int = 70) -> str:
    """Produces a clean single-line snippet from multiline chunk text."""
    clean = " ".join(text.split())
    if len(clean) > max_length:
        return clean[:max_length - 3] + "..."
    return clean


def run_retrieval_comparison():
    """Indexes sample docs, executes filtered vs unfiltered queries, and displays comparison."""
    data_dir = BACKEND_ROOT / "data" / "raw_docs"
    chroma_dir = BACKEND_ROOT / "data" / "chroma_db"

    print("================================================================================")
    print("           DOCDRIFT RETRIEVAL & VERSION-FILTER COMPARISON TEST                  ")
    print("================================================================================")

    # Step 1: Ingest sample documents
    print(f"\n[1/3] Loading documents from: {data_dir}")
    raw_docs = load_markdown_documents(data_dir)
    chunks = chunk_documents(raw_docs)
    print(f"      Generated {len(chunks)} chunks across {len(raw_docs)} files.")

    # Step 2: Index into Chroma
    print(f"[2/3] Indexing chunks into persistent Chroma store: {chroma_dir}")
    count = index_chunks(chunks=chunks, persist_dir=chroma_dir)
    print(f"      Indexed {count} chunks into collection.")

    # Step 3: Run comparative search
    query = "How do I get or fetch a user's address?"
    print(f"\n[3/3] Querying: '{query}'\n")

    # Run searches
    unfiltered_results = search(query=query, version=None, top_k=3, persist_dir=chroma_dir)
    v2_results = search(query=query, version="v2.1", top_k=3, persist_dir=chroma_dir)
    v3_results = search(query=query, version="v3.0", top_k=3, persist_dir=chroma_dir)

    # Print Side-by-Side Comparison
    col_width = 38
    divider = "-" * 80
    print(divider)
    print(f"{'UNFILTERED (Global RAG)':<{col_width}} | {'FILTERED: Version v2.1':<{col_width}}")
    print(divider)

    max_rows = max(len(unfiltered_results), len(v2_results))
    for i in range(max_rows):
        left_str = "None"
        if i < len(unfiltered_results):
            r = unfiltered_results[i]
            left_str = f"#{i+1} [{r.version}] ({r.doc_type}) {r.section[:16]}"

        right_str = "None"
        if i < len(v2_results):
            r = v2_results[i]
            right_str = f"#{i+1} [{r.version}] ({r.doc_type}) {r.section[:16]}"

        print(f"{left_str:<{col_width}} | {right_str:<{col_width}}")

    print(divider)
    print(f"{'FILTERED: Version v2.1':<{col_width}} | {'FILTERED: Version v3.0':<{col_width}}")
    print(divider)

    max_rows_v2_v3 = max(len(v2_results), len(v3_results))
    for i in range(max_rows_v2_v3):
        left_str = "None"
        if i < len(v2_results):
            r = v2_results[i]
            left_str = f"#{i+1} [{r.version}] {r.source_doc} (score:{r.similarity_score:.3f})"

        right_str = "None"
        if i < len(v3_results):
            r = v3_results[i]
            right_str = f"#{i+1} [{r.version}] {r.source_doc} (score:{r.similarity_score:.3f})"

        print(f"{left_str:<{col_width}} | {right_str:<{col_width}}")

    print(divider)

    # Print Detailed Match Breakdown
    print("\n--- Detailed Results Breakdown ---")
    print("\n[Unfiltered Results (crosses versions)]:")
    for idx, r in enumerate(unfiltered_results, 1):
        print(f"  {idx}. Version: {r.version:4} | Score: {r.similarity_score:.4f} | Source: {r.source_doc} | Section: {r.section}")
        print(f"     Snippet: {format_snippet(r.text)}")

    print("\n[Version v2.1 Filtered Results (Notice ONLY v2.1 matches returned)]:")
    for idx, r in enumerate(v2_results, 1):
        print(f"  {idx}. Version: {r.version:4} | Score: {r.similarity_score:.4f} | Source: {r.source_doc} | Section: {r.section}")
        print(f"     Snippet: {format_snippet(r.text)}")

    print("\n[Version v3.0 Filtered Results (Notice ONLY v3.0 matches returned)]:")
    for idx, r in enumerate(v3_results, 1):
        print(f"  {idx}. Version: {r.version:4} | Score: {r.similarity_score:.4f} | Source: {r.source_doc} | Section: {r.section}")
        print(f"     Snippet: {format_snippet(r.text)}")

    # Verification assertions
    assert len(unfiltered_results) > 0, "Unfiltered search returned no results"
    for r in v2_results:
        assert r.version == "v2.1", f"Expected version v2.1, got {r.version}"
    for r in v3_results:
        assert r.version == "v3.0", f"Expected version v3.0, got {r.version}"

    print("\n[SUCCESS] Retrieval and version filtering assertions passed successfully!\n")


if __name__ == "__main__":
    run_retrieval_comparison()
