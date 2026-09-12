import os
import sys
import subprocess
import time

print("=" * 70)
print("  🚀 Starting The Lenny Growth Assistant - Local Development Runner")
print("=" * 70)

backend_dir = os.path.join(os.path.dirname(__file__), "backend")
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

# 1. Run transcript ingestion
print("[1/3] Verifying transcript ingestion & index...")
subprocess.run([sys.executable, "scripts/ingest_transcripts.py"], check=True)

# 2. Starting Backend
print("\n[2/3] Launching FastAPI Backend on http://localhost:8000...")
backend_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    cwd=backend_dir
)

# 3. Starting Frontend info
print("\n[3/3] Ready! Start frontend in a separate terminal:")
print("      cd frontend && npm install && npm run dev")
print("\nAccess the application at:")
print("  👉 Frontend UI: http://localhost:5173")
print("  👉 Backend API: http://localhost:8000/docs")
print("  👉 Health:      http://localhost:8000/health")
print("=" * 70)

try:
    backend_proc.wait()
except KeyboardInterrupt:
    print("\nStopping Lenny Growth Assistant...")
    backend_proc.terminate()
