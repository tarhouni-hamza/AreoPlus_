from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.config import METRICS_PATH, MODEL_PATH
from app.ml.features import FEATURE_COLUMNS, add_features

MODEL_VERSION = "rf-baseline-v1"


def train_and_evaluate(
    train_frame: pd.DataFrame,
    evaluation_frame: pd.DataFrame,
    evaluation_targets: pd.Series,
    *,
    dataset_name: str,
    model_path: Path = MODEL_PATH,
    metrics_path: Path = METRICS_PATH,
) -> dict:
    """Fit on full training trajectories; evaluate only on held-out engines' final rows."""
    train_features = add_features(train_frame)
    eval_features = add_features(evaluation_frame)
    if "rul" not in train_features:
        raise ValueError("Training frame must contain an 'rul' target column")
    train_x = train_features[FEATURE_COLUMNS]
    train_y = train_features["rul"].clip(lower=0, upper=125)

    final_rows = eval_features.groupby("engine_id", sort=False).tail(1).sort_values("engine_id")
    targets = evaluation_targets.reset_index(drop=True)
    if len(final_rows) != len(targets):
        raise ValueError("Evaluation target count must match the number of evaluation engines")

    model = RandomForestRegressor(
        n_estimators=180,
        max_features=0.85,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train_x, train_y)
    predictions = np.clip(model.predict(final_rows[FEATURE_COLUMNS]), 0, None)
    mae = float(mean_absolute_error(targets, predictions))
    rmse = float(np.sqrt(mean_squared_error(targets, predictions)))
    r2 = float(r2_score(targets, predictions)) if len(targets) > 1 else 0.0

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "feature_columns": FEATURE_COLUMNS, "version": MODEL_VERSION}, model_path)
    metrics = {
        "model_name": "Random Forest Regressor",
        "model_version": MODEL_VERSION,
        "dataset": dataset_name,
        "evaluation_method": "Engine-level holdout; prediction at each held-out engine's latest observed cycle",
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 3),
        "evaluated_engines": int(len(targets)),
        "note": "Benchmark result, not a certified maintenance decision. Never use this model to operate real aircraft.",
    }
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def load_model(path: Path = MODEL_PATH):
    if not path.exists():
        return None
    return joblib.load(path)


def predict_latest(history: pd.DataFrame, bundle: dict) -> float:
    featured = add_features(history)
    latest = featured.groupby("engine_id", sort=False).tail(1)
    model = bundle["model"]
    value = float(model.predict(latest[bundle["feature_columns"]])[0])
    return max(0.0, value)
