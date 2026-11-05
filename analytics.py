from __future__ import annotations

from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Engine


def get_overview(db: Session) -> dict:
    engines = list(db.scalars(select(Engine).options(selectinload(Engine.observations))).all())
    counts = {"critical": 0, "watch": 0, "healthy": 0}
    for engine in engines:
        counts[engine.risk_level] = counts.get(engine.risk_level, 0) + 1

    # Compare median sensor readings at cycle buckets across the monitored fleet.
    buckets: dict[int, list[float]] = defaultdict(list)
    for engine in engines:
        for observation in engine.observations:
            if "s15" in observation.sensors:
                bucket = ((observation.cycle - 1) // 10) * 10 + 1
                buckets[bucket].append(float(observation.sensors["s15"]))
    trend = [
        {"cycle": cycle, "mean_sensor_s15": round(sum(values) / len(values), 3)}
        for cycle, values in sorted(buckets.items())
    ]
    return {
        "total_engines": len(engines),
        "critical_engines": counts.get("critical", 0),
        "watchlist_engines": counts.get("watch", 0),
        "healthy_engines": counts.get("healthy", 0),
        "average_predicted_rul": round(
            sum(e.predicted_rul for e in engines) / len(engines), 1
        ) if engines else 0.0,
        "risk_distribution": [
            {"name": "Critical", "value": counts.get("critical", 0)},
            {"name": "Watch", "value": counts.get("watch", 0)},
            {"name": "Healthy", "value": counts.get("healthy", 0)},
        ],
        "fleet_trend": trend,
    }
