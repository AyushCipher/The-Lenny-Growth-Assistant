# Product Requirements Document (PRD)
## Project: The Lenny Growth Assistant
**Role**: Forward Deployed Engineer Take-Home Assessment  
**Author**: Ayush Verma (ayushv3533e@gmail.com)  
**Status**: Approved & Active  
**Version**: 1.0.0  

---

## 1. Executive Summary & Discovery Brief

### 1.1 User & Problem Statement
- **Primary User**: Product Managers (PMs), Growth Leaders, Founders, and Forward Deployed Engineers who need authoritative, battle-tested product and growth strategies.
- **Job-to-be-Done (JTBD)**: When tackling critical strategic dilemmas (e.g., pricing optimization, retention drops, PLG vs. Sales-Led transitions, defining North Star metrics, running pre-mortems), the user needs to search across a curated corpus of high-signal Lenny’s Podcast transcripts, synthesize actionable frameworks, and produce executive-ready written essays and interactive artifacts without reading through hundreds of raw transcripts or dealing with complex prompt engineering.
- **Pain Removed**:
  - Eliminates hours of manual transcript searching and disparate note-taking.
  - Eliminates generic, hallucinated AI advice by enforcing strict transcript grounding with episode, guest, and timestamp citations.
  - Bridges the gap between static text and actionable execution by generating native, interactive HTML/CSS calculators, growth models, and PM templates directly inside a Claude-style split-pane workspace.

### 1.2 Measurable Success Metrics
1. **Citation Coverage Benchmark**: $\ge 95\%$ of factual claims in the evaluated grounded benchmark set cite specific guest names, episode titles, and timestamps/chunks.
2. **Citation Validity Benchmark**: $\ge 98\%$ of sampled citations resolve directly to the retrieved transcript evidence.
3. **Unsupported-Question Refusal Target**: $\ge 95\%$ of deliberately unsupported out-of-domain benchmark questions produce an explicit insufficient-evidence response rather than hallucinating.
4. **Ship 30 for 30 Structure Compliance**: $\ge 95\%$ compliance with Ship 30 for 30 writing principles (~1,250 words, 1-3-1 pacing, hook formula, 2-Year Test, skimmable bolding, actionable takeaway).
5. **System Latency (P95)**:
   - Hybrid RAG retrieval: $< 250\text{ ms}$
   - Local Ollama Time-to-First-Token (TTFT): $< 3.0\text{ s}$
   - Claude 3.5 Sonnet TTFT: $< 1.5\text{ s}$
6. **Artifact Security Isolation**: $100\%$ pass rate on the defined artifact security regression suite (blocking parent DOM access, parent window access, top navigation, form submissions, external network requests, external scripts, `javascript:` URIs, and XSS payloads).
7. **Operational Readiness**: Streamlined, reproducible one-command startup via Docker Compose with automated PostgreSQL provisioning and clearly documented Ollama model setup.

### 1.3 Key Assumptions
1. **Curated Transcript Knowledge Base**: The application is seeded with a curated corpus of high-signal Lenny's Podcast episodes covering foundational PM, Growth, and Leadership strategies, equipped with an automated ingestion and incremental refresh pipeline (`scripts/ingest_transcripts.py`).
2. **Local Model Availability (Demo Mandatory)**: The evaluator will run the submitted demo locally using Ollama (`http://localhost:11434` or Docker network `http://ollama:11434`) with a supported model such as `llama3`, `mistral`, `qwen2.5`, or `llama3.2`.
3. **Database Topology**: PostgreSQL is the primary persistence engine. A zero-config SQLite development fallback is built-in for instant local smoke-testing.
4. **User & Session Metadata**: User sessions are tracked via distinct UUIDs, recording timestamps, active model provider, token usage, and client metadata.

### 1.4 Scope Boundaries
- **Included**:
  - Full-stack application (FastAPI backend + React/Vite/Tailwind frontend).
  - Agent runtime built using the **Anthropic Claude Agent SDK** for agent state, tool execution, and memory orchestration.
  - Pluggable Model Provider Layer supporting Local Ollama (mandatory for demo), Anthropic Claude, and OpenAI.
  - Hybrid RAG engine (Dense vector embeddings + BM25 keyword matching + Reciprocal Rank Fusion with $k=60$).
  - Transcript refresh and incremental re-indexing pipeline with versioned source manifests (`source_manifest.json`).
  - Dedicated Ship 30 for 30 content generation skill (~1,250 words, formatted).
  - Claude-style split-pane Artifact Viewer for Markdown and self-contained sandboxed HTML/CSS widgets.
  - Structured JSON logging, error resilience, PostgreSQL persistence, and health/diagnostics endpoints.
  - Complete automated test suite (`pytest`) and manual UI test plan (`UI_TEST_PLAN.md`).
- **Intentionally Excluded & Rationale**:
  - *Real-time audio transcription*: Transcripts are pre-ingested to optimize latency and predictability.
  - *Distributed vector database clusters (Pinecone/Milvus/Qdrant Cloud)*: An in-memory/local hybrid vector+BM25 index avoids external SaaS dependencies, ensuring 100% local reproducible offline execution for the evaluator.
  - *Complex enterprise OAuth multi-tenant auth*: Session-based persistence with user metadata satisfies the take-home requirements without adding login friction for the evaluator.

### 1.5 Risk Analysis & Mitigation Matrix
| Risk | Severity | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Hallucination** | High | User acts on false product advice | 3-tier response contract; explicit grounding prompts; refusal on out-of-domain queries. |
| **Local Model Quality (Ollama)** | Medium | Output formatting degradation | Few-shot prompting, structured system instructions, top-k high-signal chunk re-ranking. |
| **Artifact Security (XSS / Untrusted HTML)** | High | Client-side execution of malicious scripts | Backend Bleach sanitization + self-contained styles + `iframe sandbox="allow-scripts"` + strict CSP `<meta>` tag (`connect-src 'none'`). |
| **Provider Latency & Timeout** | Medium | Frustrating user experience | Async streaming responses, UI loading skeletons, configurable timeouts with retry backoff. |
| **Unconfigured / Missing API Keys** | Low | Confusing runtime crashes | UI diagnostic badges clearly display provider health; system provides intuitive switch instructions and actionable diagnostic responses. |

---

## 2. User Experience & Core Workflows

### 2.1 Workflow 1: Grounded Strategic Q&A
1. User enters a growth or product question (e.g., *"How does Elena Verna recommend scaling Product-Led Growth in B2B?"*).
2. The agent extracts semantic keywords and query embeddings, querying the Hybrid RAG engine (BM25 + Dense embeddings fused via RRF with $k=60$).
3. Retrieved high-signal transcript chunks are passed to the agent runtime with strict grounding instructions.
4. The assistant streams the answer with inline citation chips (e.g., `[[Elena Verna - PLG & B2B Growth | 14:20]](src_elena_verna_01)`).
5. User clicks a citation chip to open the **Source Drawer**, inspecting the exact verbatim transcript passage and episode metadata.

### 2.2 Workflow 2: Ship 30 for 30 Essay Generation
1. User clicks the **Ship 30 for 30** button in the sidebar or requests an essay in chat.
2. The dedicated `Ship30Skill` invokes the structured prompt framework:
   - Catchy, curiosity-driven headline hook.
   - 2-Year Test framing.
   - 1-3-1 pacing cadence.
   - Skimmable formatting with bold emphasis and bullet points.
   - Grounded Lenny Podcast insights and guest quotes.
   - Actionable 3-step takeaway checklist.
3. The generated essay is validated for approximate word count (~1,250 words) and presented in the conversation feed with one-click export.

### 2.3 Workflow 3: Interactive Artifact Generation & Claude-Style Split Pane
1. User asks for a tactical template or calculator (e.g., *"Create an interactive HTML/CSS growth loop calculator based on Brian Balfour's framework"*).
2. The agent detects artifact intent and wraps the code in structured tags `:::artifact{title="..." type="html"} ... :::`.
3. The frontend parses the stream, automatically opens the **Claude-style Split Pane**, and injects the sanitized HTML into a sandboxed `<iframe>` with strict CSP meta tags.
4. The user interacts with the live calculator in the preview tab, switches to the code tab to inspect the source code, and can download the artifact as `.html` or `.md`.

---

## 3. Detailed Acceptance Criteria

| Feature Area | Acceptance Criteria |
| :--- | :--- |
| **API & Persistence** | - FastAPI backend runs with async endpoints and RFC-7807 structured error envelopes.<br>- PostgreSQL stores sessions, messages, artifacts, sources, and metrics with token usage.<br>- Sessions maintain strict independent context. |
| **Flexible LLM** | - Evaluator can toggle between Local Ollama, Anthropic Claude, and OpenAI via UI without changing code.<br>- Local Ollama is fully demonstrated as the primary demo backend.<br>- Missing API keys or offline services produce clear, actionable diagnostic alerts. |
| **Knowledge Base & RAG**| - Curated transcript corpus is parsed, chunked, and indexed with BM25 + Dense vector embeddings.<br>- Reciprocal Rank Fusion ($k=60$) combines rankings accurately.<br>- Answers strictly cite transcript sources; unsupported questions trigger polite refusal. |
| **Ship 30 for 30 Skill** | - Dedicated skill produces ~1,250-word essays following the Hook, 2-Year Test, 1-3-1 rhythm, and actionable takeaway principles grounded in transcripts. |
| **Artifact Viewer** | - Side-by-side split pane auto-opens on artifact creation.<br>- Renders Markdown and HTML/CSS natively in an isolated sandbox (`iframe sandbox="allow-scripts"` with CSP meta tag).<br>- Supports copy, export, and version switching. |
| **Observability** | - Structured JSON logs include `request_id`, `session_id`, `provider`, `model`, `input_tokens`, `output_tokens`, `total_tokens`, and latencies.<br>- `/api/diagnostics` exposes live health and performance metrics. |
| **Deployment** | - 1-command startup with `docker-compose up --build` or zero-config local run scripts. |
