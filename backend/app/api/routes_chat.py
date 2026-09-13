import uuid
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import SessionModel, MessageModel, ArtifactModel
from app.schemas.schemas import ChatRequest, ChatResponse, ArtifactResponse, TokenUsage
from app.agent.orchestrator import orchestrator
from app.observability.metrics import record_metric
from app.observability.logging import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat_completion(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    start_time = time.time()
    req_id = f"req-{uuid.uuid4().hex[:8]}"

    # 1. Resolve or Create Session
    session_id = request.session_id
    if session_id:
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            session_obj = SessionModel(id=session_id, title=request.message[:40] + "...")
            db.add(session_obj)
            await db.commit()
    else:
        session_id = str(uuid.uuid4())
        session_obj = SessionModel(
            id=session_id,
            title=request.message[:40] + "..." if len(request.message) > 40 else request.message,
            user_metadata=request.user_metadata or {}
        )
        db.add(session_obj)
        await db.commit()

    # 2. Fetch Chat History for context
    msg_result = await db.execute(
        select(MessageModel).where(MessageModel.session_id == session_id).order_by(MessageModel.timestamp)
    )
    history_models = msg_result.scalars().all()
    chat_history = [{"role": m.role, "content": m.content} for m in history_models]

    # 3. Persist User Message
    user_msg = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    await db.commit()

    # 4. Execute Grounded Agent Orchestration
    try:
        content, citations, artifacts_base, gen_result, total_latency_ms = await orchestrator.execute_chat(
            user_message=request.message,
            chat_history=chat_history,
            provider_override=request.provider
        )
    except Exception as e:
        logger.error(f"Chat execution failed: {e}", extra={"request_id": req_id, "session_id": session_id})
        await record_metric(
            db=db,
            request_id=req_id,
            endpoint="/api/chat",
            provider=request.provider or "default",
            model=request.model or "default",
            total_ms=(time.time() - start_time) * 1000.0,
            status="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(e)}"
        )

    # 5. Persist Assistant Message
    now_utc = datetime.now(timezone.utc)
    assistant_msg_id = str(uuid.uuid4())
    citations_data = [c.dict() for c in citations]
    assistant_msg = MessageModel(
        id=assistant_msg_id,
        session_id=session_id,
        role="assistant",
        content=content,
        citations=citations_data,
        model_used=f"{gen_result.provider}:{gen_result.model}",
        latency_ms=total_latency_ms,
        timestamp=now_utc,
    )
    db.add(assistant_msg)

    # 6. Persist Generated Artifacts
    created_artifact_responses: list[ArtifactResponse] = []
    for art in artifacts_base:
        art_id = str(uuid.uuid4())
        art_model = ArtifactModel(
            id=art_id,
            session_id=session_id,
            message_id=assistant_msg_id,
            title=art.title,
            type=art.type,
            content=art.content,
            sanitized_content=art.sanitized_content,
            version=1,
            created_at=now_utc
        )
        db.add(art_model)
        created_artifact_responses.append(
            ArtifactResponse(
                id=art_id,
                session_id=session_id,
                message_id=assistant_msg_id,
                title=art.title,
                type=art.type,
                content=art.content,
                sanitized_content=art.sanitized_content,
                version=1,
                created_at=now_utc
            )
        )

    await db.commit()

    # 7. Record Observability Telemetry
    token_usage = TokenUsage(
        input_tokens=gen_result.input_tokens,
        output_tokens=gen_result.output_tokens,
        total_tokens=gen_result.total_tokens
    )
    await record_metric(
        db=db,
        request_id=req_id,
        endpoint="/api/chat",
        provider=gen_result.provider,
        model=gen_result.model,
        input_tokens=gen_result.input_tokens,
        output_tokens=gen_result.output_tokens,
        total_tokens=gen_result.total_tokens,
        retrieval_count=len(citations),
        llm_ms=gen_result.latency_ms,
        total_ms=total_latency_ms,
        status="success"
    )

    logger.info(
        f"Chat response generated for session {session_id}",
        extra={
            "request_id": req_id,
            "session_id": session_id,
            "provider": gen_result.provider,
            "model": gen_result.model,
            "input_tokens": gen_result.input_tokens,
            "output_tokens": gen_result.output_tokens,
            "total_tokens": gen_result.total_tokens,
            "total_latency_ms": total_latency_ms
        }
    )

    return ChatResponse(
        session_id=session_id,
        message_id=assistant_msg_id,
        role="assistant",
        content=content,
        citations=citations,
        artifacts=created_artifact_responses,
        provider=gen_result.provider,
        model=gen_result.model,
        latency_ms=total_latency_ms,
        token_usage=token_usage
    )
