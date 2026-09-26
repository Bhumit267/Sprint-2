<div align="center">
  <img src="https://placehold.co/150x150/161A16/D5A021?text=D&font=Playfair+Display" width="100" height="100" alt="DocDrift Logo" style="border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <h1>DocDrift</h1>
  <p><strong>Version-isolated Developer Documentation Intelligence with Exact Source Citations.</strong></p>

  <p>
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#docker-deployment">Docker</a> •
    <a href="#usage-guide">Usage Guide</a>
  </p>
</div>

<br>

**DocDrift** is a modern, multi-tenant Retrieval-Augmented Generation (RAG) platform designed to solve the biggest headache in developer ecosystems: **drifted, outdated, and conflicting documentation**. 

By intelligently isolating documentation versions and grounding every AI response in exact citations, DocDrift guarantees that your team gets **zero speculation** and **100% accuracy**.

---

## ✨ Features

- **🏢 Multi-Tenant Architecture**: Isolate data across multiple organizations. Maintainers manage organizations; Admins manage users and documents.
- **📚 Version-Isolated RAG**: Stop LLM hallucinations caused by conflicting API versions. Ask questions strictly scoped to `v1.0`, `v2.0`, etc.
- **🔍 Exact Source Citations**: Every answer includes the precise markdown file and section it was extracted from.
- **🤖 Dynamic AI Suggestions**: Homepage automatically generates highly relevant suggested inquiries based on your organization's currently ingested documents.
- **⚡ Premium UI**: Fast, beautiful dark-mode Native interface powered by Next.js and Tailwind CSS.
- **🔐 Enterprise-Grade Auth**: JWT-based authentication with strict role-based access control (Maintainer, Admin, Employee).

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS (Custom thematic design system)
- **Deployment**: Docker Standalone Build

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (via Supabase) + SQLAlchemy
- **Vector Store**: ChromaDB
- **LLM/Embeddings**: Ollama Cloud (llama3.2) & LangChain

---

## 🚀 Getting Started

You can run DocDrift entirely via Docker (Recommended) or run the frontend and backend manually for development.

### 🐳 1. Docker Deployment (Recommended)

Make sure you have [Docker](https://www.docker.com/) and Docker Compose installed.

**1. Clone the repository:**
```bash
git clone https://github.com/Bhumit267/Sprint-2.git
cd Sprint-2
```

**2. Configure Environment Variables:**
Create `.env` inside `docdrift-backend/`:
```env
OLLAMA_API_KEY=your_ollama_key
OLLAMA_BASE_URL=https://ollama.com
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
SUPABASE_URL=https://your_supabase_project.supabase.co
SUPABASE_KEY=your_supabase_key
```

Create `.env.local` inside `docdrift-frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**3. Build and Start the Containers:**
```bash
docker-compose up --build -d
```
That's it! Your frontend is live at `http://localhost:3000` and the backend API is at `http://localhost:8000`.

---

### 💻 2. Manual Local Setup

If you prefer to run the services natively for development:

**Backend Setup:**
```bash
cd docdrift-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend Setup:**
```bash
cd docdrift-frontend
npm install
npm run dev
```

---

## 🧑‍💻 Usage Guide

1. **Sign Up**: Navigate to the Login page and click **Create an organization** to register a new workspace. You will automatically become the Admin.
2. **Invite Team**: Go to the **Team** tab in the navigation bar to invite other Employees or Admins to your workspace.
3. **Upload Docs**: Navigate to the **Upload** tab. Upload your markdown `.md` documentation files and tag them with a version (e.g., `v2.1`).
4. **Ask Questions**: Go to the **Chat** or Homepage. Select your target version and ask a question. The AI will instantly search your docs and synthesize a cited answer!

---

<div align="center">
  <p>Built with ❤️ by Team GroundTruth</p>
</div>
