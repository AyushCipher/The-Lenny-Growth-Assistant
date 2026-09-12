import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import init_db
from app.rag.indexer import get_hybrid_index
from app.observability.logging import setup_structured_logging, logger
from app.api.routes_chat import router as chat_router
from app.api.routes_ship30 import router as ship30_router
from app.api.routes_sessions import router as sessions_router
from app.api.routes_artifacts import router as artifacts_router
from app.api.routes_sources import router as sources_router
from app.api.routes_models import router as models_router
from app.api.routes_health import router as health_router

# Setup structured JSON logging
setup_structured_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})")
    # Initialize DB tables
    await init_db()
    # Initialize Hybrid RAG index
    index = get_hybrid_index()
    logger.info(f"Loaded RAG index with {len(index.chunks)} chunks")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Conversational AI Assistant grounded in Lenny's Podcast transcripts with Claude-style split-pane Artifact Viewer and Ship 30 for 30 skill.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global RFC-7807 Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "https://errors.lennygrowth.ai/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": str(request.url.path)
        }
    )


# Register Routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(ship30_router)
app.include_router(sessions_router)
app.include_router(artifacts_router)
app.include_router(sources_router)
app.include_router(models_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
