from __future__ import annotations

import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import METRICS_PATH
from app.database import get_db
from app.schemas import ModelMetricsOut, OverviewOut
from app.services.analytics import get_overview

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/overview", response_model=OverviewOut)
def overview(db: Session = Depends(get_db)):
    return get_overview(db)


@router.get("/model/metrics", response_model=ModelMetricsOut)
def model_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {
        "model_name": "Not trained",
        "model_version": "unavailable",
        "dataset": "No dataset loaded",
        "evaluation_method": "Run the demo bootstrap or NASA ingestion pipeline",
        "note": "Model metrics are not available yet.",
    }
