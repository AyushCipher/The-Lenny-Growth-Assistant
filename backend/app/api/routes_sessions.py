from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.db.models import SessionModel, MessageModel, ArtifactModel
from app.schemas.schemas import SessionCreate, SessionResponse, SessionDetailResponse, MessageResponse, ArtifactResponse

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    # Query sessions with message and artifact counts
    stmt = (
        select(
            SessionModel,
            func.count(MessageModel.id).label("message_count"),
        )
        .outerjoin(MessageModel, SessionModel.id == MessageModel.session_id)
        .group_by(SessionModel.id)
        .order_by(SessionModel.updated_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    session_responses = []
    for session_obj, msg_count in rows:
        # Get artifact count
        art_count_res = await db.execute(
            select(func.count(ArtifactModel.id)).where(ArtifactModel.session_id == session_obj.id)
        )
        art_count = art_count_res.scalar() or 0

        session_responses.append(
            SessionResponse(
                id=session_obj.id,
                title=session_obj.title,
                user_metadata=session_obj.user_metadata,
                created_at=session_obj.created_at,
                updated_at=session_obj.updated_at,
                message_count=msg_count,
                artifact_count=art_count
            )
        )

    return session_responses


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SessionCreate, db: AsyncSession = Depends(get_db)):
    session_obj = SessionModel(
        title=request.title or "New Strategy Chat",
        user_metadata=request.user_metadata or {}
    )
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)

    return SessionResponse(
        id=session_obj.id,
        title=session_obj.title,
        user_metadata=session_obj.user_metadata,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        message_count=0,
        artifact_count=0
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_details(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SessionModel)
        .where(SessionModel.id == session_id)
        .options(
            selectinload(SessionModel.messages),
            selectinload(SessionModel.artifacts)
        )
    )
    result = await db.execute(stmt)
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    messages_data = [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            citations=m.citations or [],
            model_used=m.model_used,
            latency_ms=m.latency_ms,
            timestamp=m.timestamp
        )
        for m in session_obj.messages
    ]

    artifacts_data = [
        ArtifactResponse(
            id=a.id,
            session_id=a.session_id,
            message_id=a.message_id,
            title=a.title,
            type=a.type,
            content=a.content,
            sanitized_content=a.sanitized_content,
            version=a.version,
            created_at=a.created_at
        )
        for a in session_obj.artifacts
    ]

    return SessionDetailResponse(
        id=session_obj.id,
        title=session_obj.title,
        user_metadata=session_obj.user_metadata,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        messages=messages_data,
        artifacts=artifacts_data
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
    session_obj = result.scalar_one_or_none()
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    await db.delete(session_obj)
    await db.commit()
    return None
