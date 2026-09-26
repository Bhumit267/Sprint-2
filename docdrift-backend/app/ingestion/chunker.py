"""Text chunking module with token-aware splitting and metadata preservation."""

import re
from typing import List, Optional
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore

from app.models.chunk import DocumentChunk, RawDocument


def extract_section_title(chunk_text: str, full_doc_text: Optional[str] = None) -> str:
    """Extracts the most relevant markdown heading for a text chunk.

    Prioritizes headings found within the chunk itself. If none exist in the chunk,
    searches backwards in the full document content prior to this chunk to find
    the prevailing parent section heading.

    Args:
        chunk_text: The chunk text to inspect.
        full_doc_text: Optional complete document content for contextual lookup.

    Returns:
        The extracted section heading string, or 'General' as a fallback.
    """
    heading_pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)

    # 1. Search inside the chunk for the first heading
    chunk_matches = list(heading_pattern.finditer(chunk_text))
    if chunk_matches:
        # Return the heading text of the first or most prominent heading in the chunk
        return chunk_matches[0].group(2).strip()

    # 2. If not found inside chunk, search backward from the chunk position in full_doc_text
    if full_doc_text:
        chunk_start = full_doc_text.find(chunk_text.strip()[:60])
        if chunk_start > 0:
            doc_prefix = full_doc_text[:chunk_start]
            prefix_matches = list(heading_pattern.finditer(doc_prefix))
            if prefix_matches:
                return prefix_matches[-1].group(2).strip()

    return "General"


def get_token_text_splitter(chunk_size: int = 500, chunk_overlap: int = 50) -> RecursiveCharacterTextSplitter:
    """Instantiates a token-aware RecursiveCharacterTextSplitter.

    Uses tiktoken cl100k_base tokenizer to count tokens accurately for OpenAI models.
    Separators are ordered to respect markdown structure (headings, double newlines,
    code blocks, lists, single newlines, spaces).

    Args:
        chunk_size: Target maximum token count per chunk (~500 tokens).
        chunk_overlap: Overlap token count between adjacent chunks (~50 tokens).

    Returns:
        Configured RecursiveCharacterTextSplitter instance.
    """
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ",
            "\n### ",
            "\n#### ",
            "\n\n",
            "\n",
            " ",
            "",
        ],
    )


def chunk_document(
    doc: RawDocument,
    org_id: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[DocumentChunk]:
    """Splits a single raw document into token-bounded chunks preserving all metadata.

    Every produced DocumentChunk contains:
    - text: segment content
    - source_doc: file name of the document
    - doc_type: inferred type (api_reference / migration_guide / changelog)
    - version: product version
    - chunk_index: zero-based index within the document
    - section: markdown heading context
    - org_id: organization ID

    Args:
        doc: The source RawDocument to be chunked.
        org_id: Organization ID.
        chunk_size: Maximum token count per chunk.
        chunk_overlap: Token overlap between adjacent chunks.

    Returns:
        List of DocumentChunk instances.
    """
    splitter = get_token_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_texts = splitter.split_text(doc.content)

    chunks: List[DocumentChunk] = []
    for idx, text in enumerate(split_texts):
        cleaned_text = text.strip()
        if not cleaned_text:
            continue

        section = extract_section_title(cleaned_text, doc.content)

        chunk = DocumentChunk(
            text=cleaned_text,
            source_doc=doc.source_doc,
            doc_type=doc.doc_type,
            version=doc.version,
            chunk_index=idx,
            section=section,
            org_id=org_id,
        )
        chunks.append(chunk)

    return chunks


def chunk_documents(
    docs: List[RawDocument],
    org_id: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[DocumentChunk]:
    """Splits a batch of raw documents into chunks preserving full metadata across all.

    Args:
        docs: List of loaded RawDocument objects.
        org_id: Organization ID.
        chunk_size: Maximum token count per chunk.
        chunk_overlap: Overlapping tokens between adjacent chunks.

    Returns:
        Flattened list of all generated DocumentChunk instances.
    """
    all_chunks: List[DocumentChunk] = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, org_id=org_id, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    return all_chunks
