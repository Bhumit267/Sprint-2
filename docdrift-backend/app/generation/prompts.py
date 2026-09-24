"""Prompt templates and context formatting for grounded LLM generation."""

from typing import Any, List, Union
from app.models.search import SearchResult


SYSTEM_PROMPT_TEMPLATE = """You are DocDrift, an expert and uncompromising technical documentation assistant.
Your job is to answer software developers' questions about version '{version}' of the product.

CRITICAL INSTRUCTIONS:
1. Grounding: Answer the question using ONLY the retrieved context excerpts provided below.
2. Version Isolation: The user is asking specifically about version '{version}'. Disregard any information about other versions unless directly asked for migration guidance.
3. No Hallucinations: If the provided context does not contain the answer, or if there is insufficient information to answer accurately for version '{version}', you MUST explicitly state that the documentation for version '{version}' does not contain this information. NEVER guess, assume, interpolate, or use prior knowledge.
4. Precision & Citations: Attribute each key instruction or endpoint detail to the specific document name and section indicated in the context headers.
"""

USER_PROMPT_TEMPLATE = """Target Version: {version}
User Question: {question}

Retrieved Documentation Context:
{formatted_context}

Please provide a clear, accurate, and version-specific answer based solely on the context above. If the context does not answer the question, state: "The documentation for version {version} does not contain information to answer this question."
"""


def format_context_chunks(chunks: List[Union[SearchResult, Any]]) -> str:
    """Formats a list of retrieved chunks into an organized context block for the prompt.

    Args:
        chunks: List of SearchResult or DocumentChunk instances.

    Returns:
        Formatted multi-line context string.
    """
    if not chunks:
        return "No matching documentation chunks retrieved."

    context_blocks: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        source_doc = getattr(chunk, "source_doc", "unknown")
        doc_type = getattr(chunk, "doc_type", "unknown")
        version = getattr(chunk, "version", "unknown")
        section = getattr(chunk, "section", "General")
        text = getattr(chunk, "text", "")

        block = (
            f"--- Context Block [{idx}] ---\n"
            f"Document: {source_doc}\n"
            f"Doc Type: {doc_type}\n"
            f"Version: {version}\n"
            f"Section: {section}\n"
            f"Content:\n{text.strip()}\n"
        )
        context_blocks.append(block)

    return "\n".join(context_blocks)
