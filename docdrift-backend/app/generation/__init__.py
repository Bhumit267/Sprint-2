"""Prompt construction, LLM generation, and citation formatting."""

from app.generation.prompts import (
    SYSTEM_PROMPT_TEMPLATE,
    USER_PROMPT_TEMPLATE,
    format_context_chunks,
)
from app.generation.generator import (
    REFUSAL_PHRASES,
    check_is_refusal,
    extract_citations,
    generate_answer,
    get_llm,
)
from app.generation.service import answer_question

__all__ = [
    "SYSTEM_PROMPT_TEMPLATE",
    "USER_PROMPT_TEMPLATE",
    "format_context_chunks",
    "REFUSAL_PHRASES",
    "check_is_refusal",
    "extract_citations",
    "generate_answer",
    "get_llm",
    "answer_question",
]
