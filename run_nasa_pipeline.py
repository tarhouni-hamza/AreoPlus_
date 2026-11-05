from __future__ import annotations

import numpy as np
import pandas as pd
from sqlalchemy import delete

from app.bootstrap_demo import seed_database
from app.config import DATA_DIR
from app.database import Base, SessionLocal, engine
from app.ml.trainer import train_and_evaluate, load_model, predict_latest

COLUMNS = ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"] + [f"s{i}" for i in range(1, 22)]


def read_cmapss(path):
    frame = pd.read_csv(path, sep=r"\s+", header=None, names=COLUMNS, engine="python")
    frame = frame.dropna(axis=1, how="all")
    frame["engine_id"] = frame["unit_id"].map(lambda value: f"NASA-TEST-{int(value):03d}" if "test_" in path.name else f"NASA-TRAIN-{int(value):03d}")
    frame = frame.drop(columns=["unit_id"])
    return frame


def run():
    raw = DATA_DIR / "raw"
    train_path = raw / "train_FD001.txt"
    test_path = raw / "test_FD001.txt"
    rul_path = raw / "RUL_FD001.txt"
    for path in (train_path, test_path, rul_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. First run: python -m app.data.download_nasa")

    train = read_cmapss(train_path)
    train["rul"] = train.groupby("engine_id")["cycle"].transform("max") - train["cycle"]
    train["rul"] = train["rul"].clip(upper=125)
    test = read_cmapss(test_path)
    true_rul = pd.read_csv(rul_path, header=None, names=["true_rul"])["true_rul"]
    test = test.sort_values(["engine_id", "cycle"]).reset_index(drop=True)
    target_order = test.groupby("engine_id", sort=True).tail(1)["engine_id"].tolist()
    targets = pd.Series(
        [int(true_rul.iloc[int(engine_id.split("-")[-1]) - 1]) for engine_id in target_order],
        dtype=float,
    )
    metrics = train_and_evaluate(
        train,
        test,
        targets,
        dataset_name="NASA C-MAPSS FD001 (simulated turbofan engine degradation)",
    )
    bundle = load_model()
    predictions = {}
    for engine_id, history in test.groupby("engine_id", sort=True):
        predictions[str(engine_id)] = predict_latest(history, bundle)
    seed_database(test, predictions)
    print("NASA C-MAPSS FD001 pipeline completed.")
    print(metrics)
    print(f"Loaded {test['engine_id'].nunique()} test engines into the dashboard database.")
    print("Evaluation targets were used for offline metrics only; they are not loaded into the dashboard database.")


if __name__ == "__main__":
    run()
