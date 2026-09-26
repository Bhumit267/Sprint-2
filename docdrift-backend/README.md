# DocDrift Backend

DocDrift is a version-aware Retrieval-Augmented Generation (RAG) system built for university sprint (Team: GroundTruth), powered by **Ollama Cloud**.

## Core Capabilities
- Ingests version-tagged API references, migration guides, and changelogs.
- Preserves chunk metadata (`source_doc`, `doc_type`, `version`, `section`) across all stages.
- Executes version-specific retrieval filtering per query.
- Emits citations with exact document, version, and section traceability.
- Refuses gracefully when no version-matching documentation exists.

## Models (Ollama Cloud)
- **Generation Model**: `llama3.2` — Meta's high-performance, lightweight instruction-tuned model.
- **Embedding Model**: `nomic-embed-text` — 768-dimensional embedding model purpose-built for RAG retrieval with 8,192 token context.

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

Copy the sample environment file:

```bash
cp .env.example .env
```

Open `.env` and configure your **Ollama Cloud** settings:
```env
OLLAMA_API_KEY=your_ollama_api_key_here
OLLAMA_BASE_URL=https://ollama.com
```

#### How to get an Ollama Cloud API Key:
1. Visit [https://ollama.com/settings/keys](https://ollama.com/settings/keys).
2. Sign in with your Ollama account.
3. Generate an API key.
4. Copy and paste it into `docdrift-backend/.env`.

### 4. Run the Backend API

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Sample Documentation Data

Sample markdown documents for testing are located under `data/raw_docs/`:
- `data/raw_docs/v2.1/`: `api_reference.md`, `changelog.md` (features `getUserAddress`, API key authentication)
- `data/raw_docs/v3.0/`: `api_reference.md`, `migration_guide.md`, `changelog.md` (renamed `getUserAddress` to `fetchAddress`, OAuth2 Bearer token auth)
- `data/raw_docs/v3.2/`: `api_reference.md`, `changelog.md` (adds `resolveNormalized` and `batchFetchAddresses`)
