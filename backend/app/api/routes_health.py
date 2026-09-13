import time
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config import settings
from app.db.database import get_db
from app.rag.indexer import get_hybrid_index
from app.rag.manifest import load_manifest
from app.observability.metrics import get_uptime_seconds, get_p95_latency_ms, get_total_requests_count
from app.schemas.schemas import HealthResponse, DiagnosticsResponse

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        timestamp=datetime.now(timezone.utc)
    )


@router.get("/api/diagnostics", response_model=DiagnosticsResponse)
async def diagnostics(db: AsyncSession = Depends(get_db)):
    # 1. Database latency
    db_ok = True
    db_start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        db_latency_ms = (time.time() - db_start) * 1000.0
    except Exception:
        db_ok = False
        db_latency_ms = 0.0

    # 2. Ollama Connectivity Check
    ollama_ok = False
    ollama_models = []
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if res.status_code == 200:
                ollama_ok = True
                ollama_models = [m.get("name") for m in res.json().get("models", [])]
    except Exception:
        ollama_ok = False

    # 3. RAG Index Stats
    index = get_hybrid_index()
    manifest = load_manifest()

    return DiagnosticsResponse(
        status="operational" if (db_ok and (ollama_ok or bool(settings.GROQ_API_KEY or settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY))) else "degraded",
        uptime_seconds=round(get_uptime_seconds(), 2),
        database_connected=db_ok,
        database_latency_ms=round(db_latency_ms, 2),
        ollama_connected=ollama_ok,
        ollama_models=ollama_models,
        anthropic_configured=bool(settings.ANTHROPIC_API_KEY),
        openai_configured=bool(settings.OPENAI_API_KEY),
        groq_configured=bool(settings.GROQ_API_KEY),
        indexed_episodes=len(manifest),
        indexed_chunks=len(index.chunks),
        index_version=index.version,
        recent_latencies_p95_ms=get_p95_latency_ms(),
        recent_requests_count=get_total_requests_count()
    )
