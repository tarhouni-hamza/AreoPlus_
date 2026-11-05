from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import delete

from app.config import DATA_DIR
from app.database import Base, SessionLocal, engine
from app.ml.trainer import load_model, predict_latest, train_and_evaluate
from app.models import Engine, EngineObservation
from app.services.risk import classify_risk

RNG_SEED = 42
SENSOR_COLUMNS = [f"s{i}" for i in range(1, 22)]


def make_trajectory(engine_no: int, total_life: int, observed_cycles: int, rng: np.random.Generator):
    engine_id = f"SIM-{engine_no:03d}"
    rows = []
    offsets = rng.normal(0, 0.6, size=21)
    slopes = rng.normal(1.0, 0.12, size=21)
    for cycle in range(1, observed_cycles + 1):
        degradation = min(1.0, cycle / total_life)
        # Sensor channels are intentionally varied to create a reproducible teaching dataset.
        values = {
            "s1": 518.67 + offsets[0] * 0.08,
            "s2": 642.0 + 7.5 * degradation * slopes[1] + rng.normal(0, 0.35),
            "s3": 1580.0 - 30.0 * degradation * slopes[2] + rng.normal(0, 1.0),
            "s4": 1400.0 + 42.0 * degradation * slopes[3] + rng.normal(0, 1.2),
            "s5": 14.62 + offsets[4] * 0.01,
            "s6": 21.61 + offsets[5] * 0.01,
            "s7": 554.0 + 6.5 * degradation * slopes[6] + rng.normal(0, 0.35),
            "s8": 2388.0 + offsets[7] * 0.01,
            "s9": 904.0 + 16.0 * degradation * slopes[8] + rng.normal(0, 0.8),
            "s10": 1.30 + offsets[9] * 0.001,
            "s11": 47.0 + 6.0 * degradation * slopes[10] + rng.normal(0, 0.25),
            "s12": 521.0 - 9.0 * degradation * slopes[11] + rng.normal(0, 0.35),
            "s13": 2388.0 + offsets[12] * 0.01,
            "s14": 813.0 + 12.0 * degradation * slopes[13] + rng.normal(0, 0.7),
            "s15": 8.40 + 1.8 * degradation * slopes[14] + rng.normal(0, 0.08),
            "s16": 0.03 + offsets[15] * 0.0001,
            "s17": 392.0 + 8.0 * degradation * slopes[16] + rng.normal(0, 0.4),
            "s18": 2388.0 + offsets[17] * 0.01,
            "s19": 100.0 + offsets[18] * 0.001,
            "s20": 39.0 + 4.5 * degradation * slopes[19] + rng.normal(0, 0.2),
            "s21": 23.0 + 3.5 * degradation * slopes[20] + rng.normal(0, 0.18),
        }
        row = {
            "engine_id": engine_id,
            "cycle": cycle,
            "setting_1": float(0.0001 + rng.normal(0, 0.00002)),
            "setting_2": float(0.0002 + rng.normal(0, 0.00002)),
            "setting_3": float(100.0 + rng.normal(0, 0.05)),
            **values,
        }
        rows.append(row)
    return rows


def generate_demo_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RNG_SEED)
    train_rows = []
    active_rows = []
    target_rows = []

    for number in range(1, 37):
        life = int(rng.integers(115, 176))
        rows = make_trajectory(number, life, life, rng)
        for row in rows:
            row["rul"] = min(125, life - row["cycle"])
        train_rows.extend(rows)

    for number in range(37, 49):
        life = int(rng.integers(120, 176))
        actual_rul = int(rng.integers(8, 91))
        observed = max(45, life - actual_rul)
        rows = make_trajectory(number, life, observed, rng)
        active_rows.extend(rows)
        target_rows.append({"engine_id": f"SIM-{number:03d}", "true_rul": actual_rul})

    train = pd.DataFrame(train_rows)
    active = pd.DataFrame(active_rows)
    targets = pd.DataFrame(target_rows).sort_values("engine_id").reset_index(drop=True)
    train.to_csv(DATA_DIR / "demo_train.csv", index=False)
    active.to_csv(DATA_DIR / "demo_active.csv", index=False)
    targets.to_csv(DATA_DIR / "demo_eval_targets.csv", index=False)
    return train, active, targets


def seed_database(active: pd.DataFrame, predictions: dict[str, float]):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.execute(delete(EngineObservation))
        db.execute(delete(Engine))
        for engine_id, history in active.groupby("engine_id", sort=True):
            history = history.sort_values("cycle")
            predicted_rul = predictions[str(engine_id)]
            latest = history.iloc[-1]
            db_engine = Engine(
                engine_id=str(engine_id),
                last_cycle=int(latest["cycle"]),
                predicted_rul=round(float(predicted_rul), 1),
                risk_level=classify_risk(float(predicted_rul)),
                model_version="rf-baseline-v1",
            )
            db.add(db_engine)
            for row in history.itertuples(index=False):
                row_values = row._asdict()
                settings = {f"setting_{i}": float(row_values[f"setting_{i}"]) for i in range(1, 4)}
                sensors = {f"s{i}": float(row_values[f"s{i}"]) for i in range(1, 22)}
                db.add(EngineObservation(
                    engine_id=str(engine_id), cycle=int(row_values["cycle"]),
                    settings=settings, sensors=sensors,
                ))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    train, active, targets = generate_demo_files()
    metrics = train_and_evaluate(
        train,
        active,
        targets["true_rul"],
        dataset_name="AeroPulse generated demonstration data (synthetic)",
    )
    bundle = load_model()
    predictions = {}
    for engine_id, history in active.groupby("engine_id", sort=True):
        predictions[str(engine_id)] = predict_latest(history, bundle)
    seed_database(active, predictions)
    print("AeroPulse demo initialized")
    print(json.dumps(metrics, indent=2))
    print(f"Seeded {active['engine_id'].nunique()} monitored engines and {len(active):,} observations.")
    print("IMPORTANT: the default demo data is synthetic. Run the NASA pipeline to use the public benchmark.")


if __name__ == "__main__":
    main()
