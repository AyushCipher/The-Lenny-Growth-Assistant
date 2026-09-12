from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import ArtifactModel
from app.schemas.schemas import ArtifactResponse

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ArtifactModel).where(ArtifactModel.id == artifact_id))
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artifact {artifact_id} not found")
    return ArtifactResponse.from_orm(artifact)


@router.get("/session/{session_id}", response_model=list[ArtifactResponse])
async def list_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ArtifactModel).where(ArtifactModel.session_id == session_id).order_by(ArtifactModel.created_at.desc())
    )
    artifacts = result.scalars().all()
    return [ArtifactResponse.from_orm(a) for a in artifacts]
