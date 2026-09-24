"""Document loading utilities for raw documentation markdown files."""

from pathlib import Path
import re
from typing import List, Union
from app.models.chunk import RawDocument


def infer_doc_type(file_name: str) -> str:
    """Infers the document type category based on the markdown file name.

    Recognizes standard documentation patterns:
    - 'api_reference' or 'api' -> 'api_reference'
    - 'migration_guide' or 'migration' -> 'migration_guide'
    - 'changelog' or 'release_notes' -> 'changelog'

    Args:
        file_name: The name of the file (e.g., 'api_reference.md').

    Returns:
        The normalized document type string.
    """
    clean_name = Path(file_name).stem.lower().replace("-", "_")

    if "api_reference" in clean_name or "api" in clean_name:
        return "api_reference"
    elif "migration_guide" in clean_name or "migration" in clean_name:
        return "migration_guide"
    elif "changelog" in clean_name or "release" in clean_name:
        return "changelog"

    return clean_name


def extract_version_from_path(file_path: Union[str, Path]) -> str:
    """Extracts product version tag from the file's folder hierarchy.

    Searches the parent directory names for a semantic version format (e.g., 'v2.1', 'v3.0.1', '2.0').
    Falls back to the immediate parent directory name if no regex match is found.

    Args:
        file_path: Path to the target file.

    Returns:
        Extracted version string (e.g., 'v2.1').
    """
    path = Path(file_path)
    # Check parent directory names from closest to furthest
    version_regex = re.compile(r"^v?\d+(\.\d+)+.*$", re.IGNORECASE)

    for parent in path.parents:
        folder_name = parent.name
        if version_regex.match(folder_name):
            return folder_name

    # Fallback to immediate parent directory name
    return path.parent.name


def load_markdown_documents(docs_dir: Union[str, Path]) -> List[RawDocument]:
    """Recursively loads all markdown documents within a directory and extracts metadata.

    For each markdown file (.md), this function:
    1. Extracts the version from the directory structure.
    2. Infers the doc_type from the file name.
    3. Reads the full text content with UTF-8 encoding.
    4. Packs the document into a typed RawDocument model.

    Args:
        docs_dir: Root directory containing version-partitioned markdown files.

    Returns:
        A list of loaded RawDocument instances, sorted by version and document name.

    Raises:
        FileNotFoundError: If the provided directory does not exist.
    """
    directory = Path(docs_dir).resolve()
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"Documentation directory not found: {directory}")

    documents: List[RawDocument] = []
    # Find all .md files recursively
    markdown_files = sorted(directory.rglob("*.md"))

    for file_path in markdown_files:
        version = extract_version_from_path(file_path)
        doc_type = infer_doc_type(file_path.name)
        content = file_path.read_text(encoding="utf-8")

        raw_doc = RawDocument(
            content=content,
            source_doc=file_path.name,
            doc_type=doc_type,
            version=version,
            file_path=str(file_path),
        )
        documents.append(raw_doc)

    return documents
