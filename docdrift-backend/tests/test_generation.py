"""Comprehensive test script executing 3 generation scenarios: success, migration/rename, and version refusal."""

import json
from pathlib import Path
import sys

# Ensure backend root is in Python sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.loader import load_markdown_documents
from app.ingestion.chunker import chunk_documents
from app.retrieval.vector_store import index_chunks
from app.generation.service import answer_question


def setup_index():
    """Ingests and indexes the sample documents into Chroma before running tests."""
    data_dir = BACKEND_ROOT / "data" / "raw_docs"
    chroma_dir = BACKEND_ROOT / "data" / "chroma_db"
    docs = load_markdown_documents(data_dir)
    chunks = chunk_documents(docs)
    index_chunks(chunks=chunks, persist_dir=chroma_dir)
    return chroma_dir


def print_case_result(case_num: int, title: str, question: str, version: str, result: dict):
    """Prints formatted test case evaluation results."""
    print("=" * 80)
    print(f"TEST CASE {case_num}: {title.upper()}")
    print("=" * 80)
    print(f"Target Version : {version}")
    print(f"User Question  : {question}\n")
    print(f"Refusal Status : {'[REFUSAL DETECTED]' if result['is_refusal'] else '[SUCCESSFULLY ANSWERED]'}")
    print("\nGenerated Answer:")
    print("-" * 80)
    print(result["answer"])
    print("-" * 80)
    print(f"\nCitations Count: {len(result['citations'])}")
    if result["citations"]:
        print("Citations:")
        for idx, c in enumerate(result["citations"], start=1):
            print(f"  [{idx}] Document: {c['source_doc']} | Version: {c['version']} | Section: {c['section']} ({c['doc_type']})")
    else:
        print("  (No citations emitted - consistent with refusal requirement)")
    print()


def run_generation_tests():
    """Runs the 3 test cases required by Prompt 4."""
    chroma_dir = setup_index()

    test_cases = [
        {
            "case_num": 1,
            "title": "Clear Success with Exact Version Citation",
            "version": "v2.1",
            "question": "How do I get a user's address in version 2.1?",
            "expect_refusal": False,
        },
        {
            "case_num": 2,
            "title": "Version Mismatch / Migration Rename Scenario",
            "version": "v3.0",
            "question": "How do I migrate getUserAddress to version 3.0, and what endpoint replaces it?",
            "expect_refusal": False,
        },
        {
            "case_num": 3,
            "title": "Version Isolation / Refusal on Non-Existent Feature",
            "version": "v2.1",
            "question": "How do I use batchFetchAddresses to retrieve multiple user addresses?",
            "expect_refusal": True,
        },
    ]

    for case in test_cases:
        res = answer_question(
            question=case["question"],
            version=case["version"],
            top_k=3,
            persist_dir=chroma_dir,
        )

        print_case_result(
            case_num=case["case_num"],
            title=case["title"],
            question=case["question"],
            version=case["version"],
            result=res,
        )

        # Verification assertions
        if case["expect_refusal"]:
            assert res["is_refusal"] is True, f"Case {case['case_num']} should have been marked as refusal"
            assert len(res["citations"]) == 0, f"Case {case['case_num']} should have empty citations on refusal"
        else:
            assert res["is_refusal"] is False, f"Case {case['case_num']} should not be a refusal"
            assert len(res["citations"]) > 0, f"Case {case['case_num']} must contain citations"
            for c in res["citations"]:
                assert c["version"] == case["version"], f"Citation version mismatch: expected {case['version']}, got {c['version']}"

    print("=" * 80)
    print("ALL 3 GENERATION & REFUSAL TEST CASES PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_generation_tests()
