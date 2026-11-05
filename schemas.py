from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EngineSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    engine_id: str
    last_cycle: int
    predicted_rul: float
    risk_level: str
    model_version: str
    updated_at: datetime


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cycle: int
    settings: dict[str, float]
    sensors: dict[str, float]


class EngineDetail(EngineSummary):
    observations: list[ObservationOut]


class OverviewOut(BaseModel):
    total_engines: int
    critical_engines: int
    watchlist_engines: int
    healthy_engines: int
    average_predicted_rul: float
    risk_distribution: list[dict]
    fleet_trend: list[dict]


class ModelMetricsOut(BaseModel):
    model_name: str
    model_version: str
    dataset: str
    evaluation_method: str
    mae: float | None = None
    rmse: float | None = None
    r2: float | None = None
    evaluated_engines: int | None = None
    note: str
