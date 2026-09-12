from fastapi import APIRouter, HTTPException, status, Query
from app.rag.manifest import load_manifest, get_source_by_id
from app.rag.loader import load_all_transcripts
from app.schemas.schemas import SourceResponse

router = APIRouter(prefix="/api/sources", tags=["Knowledge Base & Sources"])


@router.get("", response_model=list[SourceResponse])
async def list_sources(query: str = Query(None, description="Filter by guest or topic")):
    manifest = load_manifest()
    docs = load_all_transcripts()
    doc_map = {d.source_id: d for d in docs}

    sources_data: list[SourceResponse] = []
    for item in manifest:
        s_id = item.get("source_id", "")
        doc = doc_map.get(s_id)
        full_content = ""
        if doc:
            full_content = "\n\n".join([f"[{s.timestamp_str or 'N/A'}] {s.topic}:\n{s.dialogue}" for s in doc.sections])

        if query:
            q_lower = query.lower()
            guest_match = q_lower in item.get("guest", "").lower()
            topic_match = q_lower in item.get("topic", "").lower()
            title_match = q_lower in item.get("episode_title", "").lower()
            if not (guest_match or topic_match or title_match):
                continue

        sources_data.append(
            SourceResponse(
                id=s_id,
                source_reference=item.get("source_reference", ""),
                episode_id=item.get("episode_id", ""),
                episode_title=item.get("episode_title", ""),
                guest=item.get("guest", ""),
                topic=item.get("topic", ""),
                timestamp_str=None,
                content=full_content,
                metadata_json=item
            )
        )

    return sources_data


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source_details(source_id: str):
    source_meta = get_source_by_id(source_id)
    if not source_meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Source {source_id} not found in manifest")

    docs = load_all_transcripts()
    doc = next((d for d in docs if d.source_id == source_id), None)
    full_content = ""
    if doc:
        full_content = "\n\n".join([f"[{s.timestamp_str or 'N/A'}] {s.topic}:\n{s.dialogue}" for s in doc.sections])

    return SourceResponse(
        id=source_id,
        source_reference=source_meta.get("source_reference", ""),
        episode_id=source_meta.get("episode_id", ""),
        episode_title=source_meta.get("episode_title", ""),
        guest=source_meta.get("guest", ""),
        topic=source_meta.get("topic", ""),
        timestamp_str=None,
        content=full_content,
        metadata_json=source_meta
    )
