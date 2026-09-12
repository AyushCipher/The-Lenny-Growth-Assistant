import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from app.config import settings
from app.observability.logging import logger


@dataclass
class TranscriptSection:
    section_id: str
    timestamp_str: Optional[str]
    topic: str
    dialogue: str


@dataclass
class TranscriptDocument:
    source_id: str
    source_reference: str
    episode_id: str
    episode_title: str
    guest: str
    topic: str
    transcript_version: str
    sections: list[TranscriptSection]


def load_all_transcripts() -> list[TranscriptDocument]:
    transcripts_dir = settings.TRANSCRIPTS_DIR
    if not os.path.exists(transcripts_dir):
        logger.warning(f"Transcripts directory {transcripts_dir} does not exist")
        return []

    documents: list[TranscriptDocument] = []
    for filename in sorted(os.listdir(transcripts_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(transcripts_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sections = [
                        TranscriptSection(
                            section_id=sec.get("section_id", ""),
                            timestamp_str=sec.get("timestamp_str"),
                            topic=sec.get("topic", ""),
                            dialogue=sec.get("dialogue", "")
                        )
                        for sec in data.get("sections", [])
                    ]
                    doc = TranscriptDocument(
                        source_id=data.get("source_id", ""),
                        source_reference=data.get("source_reference", ""),
                        episode_id=data.get("episode_id", ""),
                        episode_title=data.get("episode_title", ""),
                        guest=data.get("guest", ""),
                        topic=data.get("topic", ""),
                        transcript_version=data.get("transcript_version", "1.0.0"),
                        sections=sections
                    )
                    documents.append(doc)
            except Exception as e:
                logger.error(f"Error loading transcript {filename}: {e}")

    logger.info(f"Loaded {len(documents)} transcript documents from {transcripts_dir}")
    return documents
