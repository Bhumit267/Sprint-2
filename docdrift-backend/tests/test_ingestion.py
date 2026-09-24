"""Tests and verification script for the DocDrift document ingestion pipeline."""

from collections import Counter
import json
from pathlib import Path
import sys

# Ensure backend root is in Python sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.loader import load_markdown_documents
from app.ingestion.chunker import chunk_documents


def run_ingestion_pipeline():
    """Executes the ingestion pipeline on sample docs and reports chunk metrics."""
    data_dir = BACKEND_ROOT / "data" / "raw_docs"
    print(f"\n--- Loading Markdown Documents from: {data_dir} ---")

    # Step 1: Load all raw documents
    documents = load_markdown_documents(data_dir)
    print(f"Loaded {len(documents)} raw documentation files:")
    for doc in documents:
        print(f"  [{doc.version}] ({doc.doc_type}) -> {doc.source_doc}")

    assert len(documents) > 0, "No markdown documents were found in raw_docs"

    # Step 2: Split documents into token-bounded chunks
    chunks = chunk_documents(documents, chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 0, "No chunks were generated"

    # Step 3: Count chunks per version
    version_counts = Counter(chunk.version for chunk in chunks)
    print("\n--- Chunks Created Per Version ---")
    for version in sorted(version_counts.keys()):
        print(f"  Version {version}: {version_counts[version]} chunk(s)")
    print(f"  Total chunks: {len(chunks)}")

    # Step 4: Validate metadata integrity on all chunks
    for chunk in chunks:
        chunk_dict = chunk.to_dict()
        assert "text" in chunk_dict and chunk_dict["text"].strip(), "Chunk text must not be empty"
        assert "source_doc" in chunk_dict and chunk_dict["source_doc"], "Missing source_doc metadata"
        assert "doc_type" in chunk_dict and chunk_dict["doc_type"], "Missing doc_type metadata"
        assert "version" in chunk_dict and chunk_dict["version"], "Missing version metadata"
        assert "chunk_index" in chunk_dict and chunk_dict["chunk_index"] is not None, "Missing chunk_index metadata"
        assert "section" in chunk_dict and chunk_dict["section"], "Missing section metadata"

    # Step 5: Print one full example chunk with metadata
    example_chunk = chunks[0]
    # Pick a chunk that demonstrates section header if available
    for c in chunks:
        if c.section not in ("General", "Overview"):
            example_chunk = c
            break

    print("\n--- Full Example Chunk with Metadata ---")
    print(json.dumps(example_chunk.to_dict(), indent=2))

    print("\n[SUCCESS] Ingestion pipeline and metadata verification passed!")
    return version_counts, chunks


def test_ingestion_pipeline():
    """Pytest test case verifying ingestion loader, chunker, and metadata integrity."""
    version_counts, chunks = run_ingestion_pipeline()
    assert "v2.1" in version_counts
    assert "v3.0" in version_counts
    assert "v3.2" in version_counts
    assert len(chunks) >= len(version_counts)


if __name__ == "__main__":
    run_ingestion_pipeline()
