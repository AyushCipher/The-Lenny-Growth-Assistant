#!/usr/bin/env bash
set -e

echo "=== Starting The Lenny Growth Assistant ==="
python scripts/ingest_transcripts.py

echo "Starting Backend..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
