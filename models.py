from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Engine(Base):
    __tablename__ = "engines"

    engine_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    last_cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_rul: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False, default="rf-baseline-v1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    observations: Mapped[list["EngineObservation"]] = relationship(
        back_populates="engine", cascade="all, delete-orphan", order_by="EngineObservation.cycle"
    )


class EngineObservation(Base):
    __tablename__ = "engine_observations"
    __table_args__ = (UniqueConstraint("engine_id", "cycle", name="uq_engine_cycle"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    engine_id: Mapped[str] = mapped_column(ForeignKey("engines.engine_id", ondelete="CASCADE"), index=True)
    cycle: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    settings: Mapped[dict] = mapped_column(JSON, nullable=False)
    sensors: Mapped[dict] = mapped_column(JSON, nullable=False)
    engine: Mapped[Engine] = relationship(back_populates="observations")
