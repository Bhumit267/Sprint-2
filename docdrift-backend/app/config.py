"""Central configuration and constants for DocDrift using Ollama Cloud."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = BASE_DIR / "data" / "raw_docs"
CHROMA_PERSIST_DIR = BASE_DIR / "data" / "chroma_db"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration (Postgres / SQLite via SQLAlchemy)
DEFAULT_DB_PATH = DATA_DIR / "docdrift.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Supabase Storage Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Authentication & JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "docdrift-secret-key-multi-tenant-secure-2026-auth")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Ollama Cloud Models & Connection
DEFAULT_GENERATION_MODEL = "gemma4:31b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_EMBEDDING_DIMENSION = 768
DEFAULT_OLLAMA_BASE_URL = "https://ollama.com"
DEFAULT_COLLECTION_NAME = "docdrift_docs"

# Configured environment settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(CHROMA_PERSIST_DIR))

GENERATION_MODEL = os.getenv("DOCDRIFT_GENERATION_MODEL", DEFAULT_GENERATION_MODEL)
EMBEDDING_MODEL = os.getenv("DOCDRIFT_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
EMBEDDING_DIMENSION = int(os.getenv("DOCDRIFT_EMBEDDING_DIMENSION", str(DEFAULT_EMBEDDING_DIMENSION)))
