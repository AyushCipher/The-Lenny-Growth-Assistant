Write-Host "=== Starting The Lenny Growth Assistant ===" -ForegroundColor Cyan
python scripts/ingest_transcripts.py

Write-Host "Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Set-Location backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
