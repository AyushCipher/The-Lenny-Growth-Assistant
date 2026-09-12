import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import SessionModel, MessageModel
from app.schemas.schemas import Ship30Request, Ship30Response, TokenUsage
from app.agent.ship30_skill import ship30_skill
from app.observability.metrics import record_metric
from app.observability.logging import logger

router = APIRouter(prefix="/api/chat/ship30", tags=["Ship 30 for 30 Skill"])


@router.post("", response_model=Ship30Response)
async def generate_ship30_essay(request: Ship30Request, db: AsyncSession = Depends(get_db)):
    start_time = time.time()
    req_id = f"req-{uuid.uuid4().hex[:8]}"

    # Resolve or create session
    session_id = request.session_id
    if session_id:
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            session_obj = SessionModel(id=session_id, title=f"Ship 30: {request.topic[:30]}")
            db.add(session_obj)
            await db.commit()
    else:
        session_id = str(uuid.uuid4())
        session_obj = SessionModel(id=session_id, title=f"Ship 30: {request.topic[:30]}")
        db.add(session_obj)
        await db.commit()

    # Save user trigger message
    user_msg = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=f"Generate Ship 30 for 30 Essay: Topic='{request.topic}', Audience='{request.target_audience}'",
    )
    db.add(user_msg)
    await db.commit()

    # Execute Ship 30 for 30 Skill
    try:
        essay_markdown, citations, gen_result = await ship30_skill.generate_essay(
            topic=request.topic,
            target_audience=request.target_audience,
            core_takeaway=request.core_takeaway,
            guest_focus=request.guest_focus,
            provider_override=request.provider
        )
    except Exception as e:
        logger.error(f"Ship 30 skill failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ship 30 for 30 generation failed: {str(e)}"
        )

    # Word count estimation
    words = essay_markdown.split()
    word_count = len(words)
    total_latency_ms = (time.time() - start_time) * 1000.0

    # Save assistant message
    assistant_msg_id = str(uuid.uuid4())
    citations_data = [c.dict() for c in citations]
    assistant_msg = MessageModel(
        id=assistant_msg_id,
        session_id=session_id,
        role="assistant",
        content=essay_markdown,
        citations=citations_data,
        model_used=f"{gen_result.provider}:{gen_result.model}",
        latency_ms=total_latency_ms,
    )
    db.add(assistant_msg)
    await db.commit()

    # Record metric
    token_usage = TokenUsage(
        input_tokens=gen_result.input_tokens,
        output_tokens=gen_result.output_tokens,
        total_tokens=gen_result.total_tokens
    )
    await record_metric(
        db=db,
        request_id=req_id,
        endpoint="/api/chat/ship30",
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

    # Extract title from first line if available
    lines = [l.strip() for l in essay_markdown.split("\n") if l.strip()]
    first_line = lines[0].replace("#", "").strip() if lines else request.topic

    return Ship30Response(
        session_id=session_id,
        message_id=assistant_msg_id,
        title=first_line,
        essay_markdown=essay_markdown,
        word_count=word_count,
        citations=citations,
        provider=gen_result.provider,
        model=gen_result.model,
        latency_ms=total_latency_ms,
        token_usage=token_usage
    )
