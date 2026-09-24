# DocDrift Backend

DocDrift is a version-aware Retrieval-Augmented Generation (RAG) system built for university sprint (Team: GroundTruth).

## Core Capabilities
- Ingests version-tagged API references, migration guides, and changelogs.
- Preserves chunk metadata (`source_doc`, `doc_type`, `version`, `section`) across all stages.
- Executes version-specific retrieval filtering per query.
- Emits citations with exact document, version, and section traceability.
- Refuses gracefully when no version-matching documentation exists.
