import os
import sys
import json
from datetime import datetime, timezone

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.config import settings
from app.rag.manifest import calculate_file_hash, load_manifest, save_manifest
from app.rag.indexer import get_hybrid_index
from app.observability.logging import logger


def run_ingestion():
    print("=== Running Lenny's Podcast Transcript Ingestion Pipeline ===")
    transcripts_dir = settings.TRANSCRIPTS_DIR
    if not os.path.exists(transcripts_dir):
        print(f"Error: Transcripts directory {transcripts_dir} not found!")
        sys.exit(1)

    manifest = load_manifest()
    manifest_map = {item["source_id"]: item for item in manifest}

    updated_count = 0
    added_count = 0

    for filename in sorted(os.listdir(transcripts_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(transcripts_dir, filename)
            file_hash = calculate_file_hash(filepath)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            source_id = data.get("source_id")
            if not source_id:
                continue

            existing = manifest_map.get(source_id)
            if existing is None:
                # New transcript
                new_entry = {
                    "source_id": source_id,
                    "source_reference": data.get("source_reference", f"Lenny's Podcast {data.get('episode_id', '')}"),
                    "episode_id": data.get("episode_id", "EP_UNKNOWN"),
                    "episode_title": data.get("episode_title", "Untitled Episode"),
                    "guest": data.get("guest", "Unknown Guest"),
                    "topic": data.get("topic", "General"),
                    "transcript_version": data.get("transcript_version", "1.0.0"),
                    "source_hash": file_hash,
                    "ingested_at": datetime.now(timezone.utc).isoformat()
                }
                manifest.append(new_entry)
                manifest_map[source_id] = new_entry
                added_count += 1
                print(f"[NEW] Ingested: {data.get('episode_title')} (Guest: {data.get('guest')})")
            elif existing.get("source_hash") != file_hash:
                # Updated transcript
                existing["source_hash"] = file_hash
                existing["transcript_version"] = data.get("transcript_version", "1.0.1")
                existing["ingested_at"] = datetime.now(timezone.utc).isoformat()
                updated_count += 1
                print(f"[UPDATED] Re-ingested: {data.get('episode_title')} (Guest: {data.get('guest')})")

    save_manifest(manifest)
    print(f"Ingestion complete: {added_count} added, {updated_count} updated. Total manifest sources: {len(manifest)}")

    # Rebuild hybrid index
    print("Rebuilding in-memory hybrid search index...")
    index = get_hybrid_index()
    index.build_index()
    print(f"Index successfully rebuilt with {len(index.chunks)} searchable chunks.")


if __name__ == "__main__":
    run_ingestion()
