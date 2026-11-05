from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Engine
from app.schemas import EngineDetail, EngineSummary

router = APIRouter(prefix="/api/engines", tags=["engines"])


@router.get("", response_model=list[EngineSummary])
def list_engines(
    risk: str | None = Query(default=None, pattern="^(critical|watch|healthy)$"),
    search: str | None = Query(default=None, min_length=1, max_length=32),
    sort: str = Query(default="predicted_rul", pattern="^(predicted_rul|engine_id|last_cycle)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    statement = select(Engine)
    if risk:
        statement = statement.where(Engine.risk_level == risk)
    if search:
        statement = statement.where(Engine.engine_id.ilike(f"%{search}%"))
    column = getattr(Engine, sort)
    statement = statement.order_by(column.asc() if order == "asc" else column.desc()).limit(limit)
    return list(db.scalars(statement).all())


@router.get("/{engine_id}", response_model=EngineDetail)
def engine_detail(engine_id: str, db: Session = Depends(get_db)):
    engine = db.scalar(
        select(Engine).where(Engine.engine_id == engine_id).options(selectinload(Engine.observations))
    )
    if engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")
    return engine
