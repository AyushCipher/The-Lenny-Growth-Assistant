import os
import json
import hashlib
from typing import Optional
from app.config import settings
from app.observability.logging import logger


def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()[:16]


def load_manifest() -> list[dict]:
    if not os.path.exists(settings.MANIFEST_PATH):
        logger.warning(f"Manifest not found at {settings.MANIFEST_PATH}, returning empty list")
        return []
    with open(settings.MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest_data: list[dict]):
    os.makedirs(os.path.dirname(settings.MANIFEST_PATH), exist_ok=True)
    with open(settings.MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    logger.info(f"Saved manifest with {len(manifest_data)} sources")


def get_source_by_id(source_id: str) -> Optional[dict]:
    manifest = load_manifest()
    for item in manifest:
        if item.get("source_id") == source_id:
            return item
    return None
