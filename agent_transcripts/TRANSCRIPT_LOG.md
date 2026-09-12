# Engineering Agent Transcripts & Build Log
**Project**: The Lenny Growth Assistant  
**Author / Engineer**: Ayush Verma (ayushv3533e@gmail.com)  
**Date**: September 2026  

---

## 1. Overview & Purpose
This document records the design decisions, engineering trajectory, failed attempts, debugging corrections, and secret-scrubbing verification conducted during the development of **The Lenny Growth Assistant**.

---

## 2. Trajectory & Engineering Decision Log

### 2.1 Decision: Hybrid Retrieval Engine Selection
- **Initial Consideration**: Utilizing an external cloud vector database (e.g. Pinecone or Qdrant Cloud).
- **Evaluation & Rejection**: Introducing third-party SaaS vector databases violates the requirement for a fully local, self-contained, offline-evaluable system and adds brittle API dependencies during evaluator review.
- **Adopted Solution**: Implemented a localized hybrid retrieval engine combining BM25 keyword indexing + normalized dense semantic embeddings fused using Reciprocal Rank Fusion ($k=60$).

### 2.2 Attempt & Correction: RRF Formula Correction
- **Issue**: During early technical review, a typographic error in the reciprocal rank fusion formulation was identified where the smoothing factor and denominator were improperly rendered (`160 + rank` rather than `1 / (60 + rank)`).
- **Correction**: Replaced with the exact mathematical formulation:
  $$RRF(d) = \frac{1}{60 + \text{rank}_{BM25}(d)} + \frac{1}{60 + \text{rank}_{Dense}(d)}$$
  Added a deterministic unit test in `backend/tests/test_rag.py` verifying that $\text{rank}_{BM25}=1$ and $\text{rank}_{Dense}=3$ yields $\frac{1}{61} + \frac{1}{63} \approx 0.032266$.

### 2.3 Attempt & Correction: Docker $\leftrightarrow$ Ollama Networking
- **Issue**: Initial container networking used `http://localhost:11434` across both host and container environments. Inside a Docker container, `localhost` points to the container itself rather than the host or sibling Ollama service.
- **Correction**: Configured dynamic networking in `config.py`:
  - In Docker Compose: `OLLAMA_BASE_URL=http://ollama:11434`
  - On Host / Local Dev: `OLLAMA_BASE_URL=http://localhost:11434`
  - In Docker referencing Host: `http://host.docker.internal:11434`

### 2.4 Attempt & Correction: Artifact Sandbox & External CDN Removal
- **Issue**: An earlier frontend prototype linked `https://cdn.tailwindcss.com` inside the artifact iframe for styling. Loading external scripts inside an untrusted user-generated artifact violates strict zero-trust sandbox boundaries.
- **Correction**: Removed external CDN dependencies. Styled elements now use self-contained inline CSS styles or scoped stylesheets. Injected a strict Content Security Policy `<meta>` header (`default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none';`) and rendered inside `<iframe sandbox="allow-scripts">` without `allow-same-origin`.

### 2.5 Attempt & Correction: Token Usage Tracking in Observability
- **Issue**: Database metric models tracked execution latency but lacked dedicated fields for input and output token counts.
- **Correction**: Updated `SystemMetricModel` and structured JSON logs to include `input_tokens`, `output_tokens`, and `total_tokens` (nullable integers), gracefully handling providers that do not emit token stream telemetry.

---

## 3. Security & Secret Scrubbing Verification
- Verified that no live API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`), database passwords, or personal credentials are hardcoded in the codebase or git commit history.
- `.env.example` provides clean, safe defaults.
- All git commits are strictly attributed to `Ayush Verma <ayushv3533e@gmail.com>`.
