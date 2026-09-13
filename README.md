# 🚀 The Lenny Growth Assistant
> **Forward Deployed Engineer Take-Home Assessment**  
> **Author**: Ayush Verma (`ayushv3533e@gmail.com`)  
> **Repository**: [https://github.com/AyushCipher/The-Lenny-Growth-Assistant](https://github.com/AyushCipher/The-Lenny-Growth-Assistant)  
> **Demo Walkthrough Video**: [YouTube Walkthrough (Camera Enabled)](https://youtube.com/watch?v=YOUR_DEMO_VIDEO_ID_HERE)

---

## 📌 Executive Summary

**The Lenny Growth Assistant** is an enterprise-grade, conversational AI platform grounded in transcripts from *Lenny's Podcast*. Designed for Product Managers, Growth Leaders, Founders, and Forward Deployed Engineers, it eliminates hours of disparate research by synthesizing battle-tested product strategies, generating viral **Ship 30 for 30** atomic essays, and rendering native, interactive **HTML/CSS and Markdown artifacts** directly within a Claude-style split-pane workspace.

### Key Highlights
- **Strict Transcript Grounding**: 3-tier answering logic with verified citations (`[[Guest - Episode | Timestamp]](source_id)`) and zero hallucination on out-of-domain topics.
- **Anthropic Claude Agent SDK Runtime**: Explicit state machine, session context memory, tool execution (`search_transcripts`, `format_ship30_essay`, `create_artifact`), and grounding verification.
- **Local Ollama Integration (Mandatory for Demo)**: First-class local offline execution (`llama3`, `mistral`, `qwen2.5`) with dynamic model provider switching to Anthropic Claude and OpenAI.
- **Hybrid RAG & Mathematical RRF ($k=60$)**: Combines BM25 keyword matching with dense semantic embeddings fused via standard Reciprocal Rank Fusion:
  $$RRF(d) = \sum_{m \in \{BM25, Dense\}} \frac{1}{60 + \text{rank}_m(d)} = \frac{1}{60 + \text{rank}_{BM25}(d)} + \frac{1}{60 + \text{rank}_{Dense}(d)}$$
- **Ship 30 for 30 Content Skill**: Dedicated engine producing ~1,250-word atomic essays adhering to the Hook formula, 2-Year Test, 1-3-1 cadence, bold emphasis, and actionable checklists.
- **Claude-Style In-App Artifact Viewer**: Split-pane interface rendering sandboxed interactive HTML/CSS widgets with strict CSP isolation (`connect-src 'none'`) and `iframe sandbox="allow-scripts"`.
- **Full PostgreSQL Persistence**: Sessions, messages, artifacts, sources, and telemetry with token usage metrics stored in PostgreSQL with SQLite local smoke-test fallback.
- **Operational Readiness**: 1-command Docker Compose startup, comprehensive structured JSON logging, and full automated `pytest` suite.

---

## 🏗️ System Architecture

```
                    FastAPI Gateway (/api/chat, /api/chat/ship30)
                                    ↓
                            Agent Orchestrator
                                    ↓
                        Anthropic Claude Agent SDK
                                    ↓
                              Tool Registry
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            search_transcripts  format_ship30  create_artifact
             (Hybrid RAG/RRF)  (Writing Engine) (Sanitizer+CSP)
                    ↓
        Application Provider Interface (`models.py`)
           ┌────────────────┼────────────────┐
           ↓                ↓                ↓
      Local Ollama       Anthropic         OpenAI
    (Mandatory Demo)    Claude SDK          SDK
```

---

## ⚡ Quickstart Guide (1-Command Docker Compose)

The fastest and most reproducible way for an evaluator to run the entire stack is via Docker Compose:

### Step 1: Clone Repository & Setup Environment
```bash
git clone https://github.com/ayushverma/lenny-growth-assistant.git
cd lenny-growth-assistant
cp .env.example .env
```

### Step 2: Launch with Docker Compose
```bash
docker compose up --build
```

### Step 3: Pull Ollama Demo Model
In a separate terminal, pull the demo model into the running Ollama container:
```bash
docker exec -it lenny-ollama ollama pull llama3
```

### Step 4: Access the Application
- 🖥️ **Frontend Web Workspace**: [http://localhost:5173](http://localhost:5173)
- 🔌 **FastAPI Backend Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📊 **Health & Telemetry Endpoint**: [http://localhost:8000/api/diagnostics](http://localhost:8000/api/diagnostics)

---

## 💻 Local Host Development Setup (Alternative)

If you prefer running directly on your host machine without Docker:

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Ollama installed locally ([https://ollama.com](https://ollama.com))

### 1. Install Backend Dependencies & Ingest Transcripts
```bash
cd backend
pip install -r requirements.txt
cd ..
python scripts/ingest_transcripts.py
```

### 2. Start Local Ollama
```bash
ollama serve
ollama pull llama3
```

### 3. Start FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start React Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🛡️ Artifact Security & Sandbox Isolation

To protect users against untrusted generated HTML/CSS, the application enforces defense-in-depth isolation:

| Capability | Status | Rationale |
| :--- | :--- | :--- |
| **HTML/CSS Rendering** | **Allowed** | Core requirement for artifact preview |
| **Local JavaScript (Math/DOM)** | **Allowed** | Required for interactive calculators and widgets |
| **Canvas 2D Graphics** | **Allowed** | Enables dynamic charts and metric graphs |
| **Parent Window Access** | **BLOCKED** | Sandbox lacks `allow-same-origin`, preventing DOM tampering |
| **Cookies & LocalStorage** | **BLOCKED** | Sandbox treats iframe as unique origin, blocking credential access |
| **Top Navigation** | **BLOCKED** | Sandbox lacks `allow-top-navigation`, preventing host redirects |
| **Form Submissions** | **BLOCKED** | Sandbox lacks `allow-forms`, eliminating phishing vectors |
| **Network Requests (Fetch/XHR)** | **BLOCKED** | Injected CSP `connect-src 'none'` prevents exfiltrating user data |
| **External Scripts / CDNs** | **BLOCKED** | Injected CSP `script-src 'unsafe-inline'` blocks third-party scripts |

---

## 🧪 Automated Testing Suite

Run the complete backend test suite covering API contracts, RAG retrieval, RRF ranking calculation ($k=60$), model switching, Ship 30 structure, database persistence, and security sanitization:

```bash
pytest backend/tests/ -v
```

### Test Coverage Highlights
- `test_api.py`: Health, diagnostics, session endpoints, source queries.
- `test_rag.py`: Dialogue chunking, BM25 + Vector hybrid retrieval, mathematical RRF calculation verification ($k=60$).
- `test_models.py`: Provider abstraction switching, Ollama/Claude/OpenAI adapters, token usage normalization.
- `test_ship30.py`: ~1,250-word essay structure, Hook, 1-3-1 pacing, bolding, transcript citations.
- `test_persistence.py`: Independent session context isolation, message history, user metadata retention.
- `test_security.py`: Malicious script stripping, event-handler neutralization, CSP meta injection.

---

## 📚 Deliverables Index

1. [PRD.md](file:///PRD.md): Complete Product Requirements Document & Discovery Brief.
2. [design.md](file:///design.md): UI/UX Design System, Split-Pane Architecture, and WCAG 2.1 AA Accessibility.
3. [architecture.md](file:///architecture.md): Technical Architecture, Database Schemas, and RRF Math.
4. [TRANSCRIPT_LOG.md](file:///agent_transcripts/TRANSCRIPT_LOG.md): Coding agent trajectory, failed attempts, and debugging log.
5. [UI_TEST_PLAN.md](file:///tests/UI_TEST_PLAN.md): Step-by-step manual UI verification checklist.

---

## 👤 Author & Git Attribution
- **Author**: Ayush Verma
- **Email**: `ayushv3533e@gmail.com`
- **Role**: Forward Deployed Engineer
