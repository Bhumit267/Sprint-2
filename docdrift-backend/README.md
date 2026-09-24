# DocDrift Backend

DocDrift is a version-aware Retrieval-Augmented Generation (RAG) system built for university sprint (Team: GroundTruth).

## Core Capabilities
- Ingests version-tagged API references, migration guides, and changelogs.
- Preserves chunk metadata (`source_doc`, `doc_type`, `version`, `section`) across all stages.
- Executes version-specific retrieval filtering per query.
- Emits citations with exact document, version, and section traceability.
- Refuses gracefully when no version-matching documentation exists.

## Getting Started

### 1. Create and Activate Virtual Environment

From the `docdrift-backend` directory:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the sample environment file and set your OpenAI API key:

```bash
cp .env.example .env
```

Open `.env` and provide your API key:
```env
OPENAI_API_KEY=your_key_here
```

## Sample Documentation Data

Sample markdown documents for testing are located under `data/raw_docs/`:
- `data/raw_docs/v2.1/`: `api_reference.md`, `changelog.md` (features `getUserAddress`, API key authentication)
- `data/raw_docs/v3.0/`: `api_reference.md`, `migration_guide.md`, `changelog.md` (renamed `getUserAddress` to `fetchAddress`, OAuth2 Bearer token auth)
- `data/raw_docs/v3.2/`: `api_reference.md`, `changelog.md` (adds `resolveNormalized` and `batchFetchAddresses`)
