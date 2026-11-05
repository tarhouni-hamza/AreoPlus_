from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'aeropulse.db').as_posix()}")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
MODEL_PATH = ARTIFACTS_DIR / "rul_model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "model_metrics.json"
RISK_CRITICAL_CYCLES = int(os.getenv("RISK_CRITICAL_CYCLES", "20"))
RISK_WATCH_CYCLES = int(os.getenv("RISK_WATCH_CYCLES", "50"))
