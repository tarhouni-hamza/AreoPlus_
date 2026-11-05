from __future__ import annotations

import pandas as pd

BASE_FEATURES = ["cycle", "setting_1", "setting_2", "setting_3"] + [f"s{i}" for i in range(1, 22)]
ROLLING_SENSORS = [2, 3, 4, 7, 8, 9, 11, 12, 13, 14, 15, 17, 20, 21]
FEATURE_COLUMNS = BASE_FEATURES + [
    f"s{i}_{stat}_5"
    for i in ROLLING_SENSORS
    for stat in ("mean", "std")
]


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create strictly historical rolling features (no centered/future windows)."""
    required = {"engine_id", *BASE_FEATURES}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required feature columns: {sorted(missing)}")

    result = frame.copy().sort_values(["engine_id", "cycle"]).reset_index(drop=True)
    for sensor in ROLLING_SENSORS:
        column = f"s{sensor}"
        grouped = result.groupby("engine_id", sort=False)[column]
        result[f"{column}_mean_5"] = grouped.transform(
            lambda values: values.rolling(window=5, min_periods=1).mean()
        )
        result[f"{column}_std_5"] = grouped.transform(
            lambda values: values.rolling(window=5, min_periods=1).std().fillna(0)
        )
    return result
