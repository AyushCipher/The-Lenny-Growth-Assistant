from dataclasses import dataclass
from typing import Optional
from app.rag.loader import TranscriptDocument


@dataclass
class TranscriptChunk:
    chunk_id: str
    source_id: str
    source_reference: str
    episode_id: str
    episode_title: str
    guest: str
    topic: str
    timestamp_str: Optional[str]
    content: str
    context_header: str

    @property
    def full_searchable_text(self) -> str:
        return f"{self.context_header}\n{self.content}"


def chunk_transcript_document(doc: TranscriptDocument) -> list[TranscriptChunk]:
    chunks: list[TranscriptChunk] = []

    for idx, sec in enumerate(doc.sections):
        context_header = (
            f"Episode: {doc.episode_title} (Guest: {doc.guest}) "
            f"| Topic: {sec.topic} | Timestamp: {sec.timestamp_str or 'N/A'}"
        )
        chunk = TranscriptChunk(
            chunk_id=f"{doc.source_id}_chunk_{idx + 1}",
            source_id=doc.source_id,
            source_reference=doc.source_reference,
            episode_id=doc.episode_id,
            episode_title=doc.episode_title,
            guest=doc.guest,
            topic=sec.topic,
            timestamp_str=sec.timestamp_str,
            content=sec.dialogue.strip(),
            context_header=context_header
        )
        chunks.append(chunk)

    return chunks


def chunk_all_documents(docs: list[TranscriptDocument]) -> list[TranscriptChunk]:
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_transcript_document(doc))
    return all_chunks
