# Technical Architecture: The Lenny Growth Assistant
**Role**: Forward Deployed Engineer Take-Home Assessment  
**Author**: Ayush Verma (ayushv3533e@gmail.com)  
**Status**: Approved & Active  
**Version**: 1.0.0  

---

## 1. System Topology & Architecture Overview

```
                      +------------------------------------------+
                      |         Frontend Client (React 18)       |
                      |   - Split-Pane Chat & Artifact Viewer    |
                      |   - Model Selector & Status Diagnostics  |
                      |   - Transcript Source Inspector Drawer   |
                      +--------------------+---------------------+
                                           | HTTP / REST / SSE
                                           v
                      +------------------------------------------+
                      |          FastAPI API Gateway             |
                      |   - Structured JSON Logging & Interceptor|
                      |   - RFC-7807 Error Envelopes & CORS      |
                      +--------------------+---------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |    Anthropic Claude Agent SDK Runtime    |
                      |   - State Machine, Memory, & Tool Loop   |
                      |   - Strict Grounding Verification        |
                      +----+---------------+----------------+----+
                           |               |                |
             +-------------+               |                +-------------+
             v                             v                              v
+------------------------+   +---------------------------+   +-------------------------+
|     RAG Tool Layer     |   |   Ship 30 for 30 Skill    |   |  Artifact Extractor     |
| - Hybrid BM25 + Vector |   | - ~1,250 Words Pacing     |   | - HTML/Markdown Parser  |
| - RRF Ranking (k=60)   |   | - 1-3-1 Cadence & Bolding |   | - Bleach Sanitizer + CSP|
| - Source Provenance    |   | - Transcript Citations    |   | - Sandboxed iframe      |
+------------+-----------+   +-------------+-------------+   +-------------------------+
             |                             |
             +--------------------+--------+
                                  |
                                  v
                      +------------------------------------------+
                      |    Application Model Provider Layer      |
                      |   - Unified Common Provider Interface    |
                      +----+---------------+----------------+----+
                           |               |                |
             +-------------+               |                +-------------+
             v                             v                              v
+------------------------+   +---------------------------+   +-------------------------+
|  Local Ollama Adapter  |   |   Anthropic Claude SDK    |   |    OpenAI API Adapter   |
| (Mandatory Demo Model) |   | (claude-3-5-sonnet/haiku) |   |    (gpt-4o / gpt-4o-mini|
| http://ollama:11434    |   | Official Anthropic Client |   | Official OpenAI Client  |
+------------------------+   +---------------------------+   +-------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |         Persistence Layer                |
                      |   - PostgreSQL (Docker / Supabase)       |
                      |   - Auto SQLite Local Dev Fallback       |
                      |   - Sessions, Messages, Artifacts, Stems |
                      +------------------------------------------+
```

---

## 2. Database Schema (PostgreSQL with SQLAlchemy)

### 2.1 Entity Relationship Diagram
```
  +------------------+         +--------------------+         +--------------------+
  |     sessions     | 1     * |      messages      | 1     * |     artifacts      |
  +------------------+---------+--------------------+---------+--------------------+
  | id (UUID, PK)    |         | id (UUID, PK)      |         | id (UUID, PK)      |
  | title (VARCHAR)  |         | session_id (FK)    |         | session_id (FK)    |
  | user_metadata    |         | role (VARCHAR)     |         | message_id (FK)    |
  |   (JSONB)        |         | content (TEXT)     |         | title (VARCHAR)    |
  | created_at (TS)  |         | citations (JSONB)  |         | type (VARCHAR)     |
  | updated_at (TS)  |         | model_used (STR)   |         | content (TEXT)     |
  +------------------+         | latency_ms (FLOAT) |         | sanitized_content  |
                               | timestamp (TS)     |         | version (INT)      |
                               +--------------------+         | created_at (TS)    |
                                                              +--------------------+

  +-----------------------+                         +-----------------------+
  |        sources        |                         |    system_metrics     |
  +-----------------------+                         +-----------------------+
  | id (VARCHAR, PK)      |                         | id (UUID, PK)         |
  | source_reference (STR)|                         | request_id (VARCHAR)  |
  | episode_id (VARCHAR)  |                         | endpoint (VARCHAR)    |
  | episode_title (STR)   |                         | provider (VARCHAR)    |
  | guest (VARCHAR)       |                         | model (VARCHAR)       |
  | topic (VARCHAR)       |                         | input_tokens (INT)    |
  | timestamp_str (STR)   |                         | output_tokens (INT)   |
  | content (TEXT)        |                         | total_tokens (INT)    |
  | metadata (JSONB)      |                         | retrieval_count (INT) |
  +-----------------------+                         | retrieval_ms (FLOAT)  |
                                                    | llm_ms (FLOAT)        |
                                                    | total_ms (FLOAT)      |
                                                    | status (VARCHAR)      |
                                                    | timestamp (TS)        |
                                                    +-----------------------+
```

---

## 3. Hybrid RAG & Ingestion Lifecycle

### 3.1 Reciprocal Rank Fusion (RRF) Formulation
To combine dense semantic retrieval and sparse BM25 keyword matching with high precision, the system applies Reciprocal Rank Fusion with smoothing factor $k = 60$:

$$RRF(d) = \sum_{m \in \{BM25, Dense\}} \frac{1}{60 + \text{rank}_m(d)} = \frac{1}{60 + \text{rank}_{BM25}(d)} + \frac{1}{60 + \text{rank}_{Dense}(d)}$$

- **Deterministic Example**: If a chunk ranks 1st in BM25 ($\text{rank}_{BM25}=1$) and 3rd in Dense embeddings ($\text{rank}_{Dense}=3$):
  $$RRF(d) = \frac{1}{60 + 1} + \frac{1}{60 + 3} = \frac{1}{61} + \frac{1}{63} \approx 0.016393 + 0.015873 = 0.032266$$

### 3.2 Ingestion & Incremental Refresh Pipeline
```
  [scripts/ingest_transcripts.py]
               ↓
  Scans data/lenny_transcripts/*.json
               ↓
  Computes SHA256 hashes vs data/source_manifest.json
               ↓
  Extracts Dialogue, Guest Name, Episode Title, Topic, Timestamps
               ↓
  Chunks Dialogue (400-600 tokens, 100-token semantic overlap)
               ↓
  Generates Dense Vector Embeddings + Builds BM25 Token Inverted Index
               ↓
  Updates Manifest & Saves Serialized Hybrid Index with Version Tag
```

---

## 4. Model Provider Abstraction & Networking

### 4.1 Networking & Container Topology
- **Docker Compose Mode**:
  - Frontend: `http://localhost:5173`
  - Backend API: `http://localhost:8000`
  - PostgreSQL: `postgres:5432` (`postgresql+asyncpg://postgres:postgres@postgres:5432/lenny_growth`)
  - Local Ollama: `http://ollama:11434`
- **Host Development Mode**:
  - Backend API: `http://localhost:8000`
  - Local Ollama: `http://localhost:11434`
  - Database: Local PostgreSQL or automatic fallback to SQLite (`sqlite+aiosqlite:///./lenny_growth.db`)

### 4.2 Unified Model Adapter Contract
```python
class BaseModelAdapter(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str,
        stream: bool = False
    ) -> GenerationResult:
        """
        Returns GenerationResult:
        - text: str
        - input_tokens: Optional[int]
        - output_tokens: Optional[int]
        - total_tokens: Optional[int]
        - latency_ms: float
        - provider: str
        - model: str
        """
        pass
```

---

## 5. Security & Artifact Sandbox Specification

1. **Content Sanitization**: Inbound HTML/CSS is parsed and stripped of dangerous tags (`<script>`, `<iframe>`, `<object>`, `<embed>`) and inline event handlers (`onload`, `onerror`, `onclick`).
2. **CSP Meta Header**: Injected into every rendered document:
   ```html
   <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; frame-src 'none'; font-src 'none';">
   ```
3. **Sandbox Attributes**: The host page renders untrusted artifacts exclusively via:
   ```html
   <iframe sandbox="allow-scripts" srcdoc="..." />
   ```
   *Strictly excludes* `allow-same-origin`, `allow-top-navigation`, and `allow-forms`.
