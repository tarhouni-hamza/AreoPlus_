import pandas as pd

from app.ml.features import add_features


def test_rolling_features_use_only_current_and_past_rows():
    rows = []
    for cycle, sensor_value in [(1, 10.0), (2, 20.0), (3, 30.0)]:
        rows.append({
            "engine_id": "TEST-1", "cycle": cycle,
            "setting_1": 0.0, "setting_2": 0.0, "setting_3": 0.0,
            **{f"s{i}": sensor_value if i == 2 else 1.0 for i in range(1, 22)},
        })
    featured = add_features(pd.DataFrame(rows))
    assert featured.loc[0, "s2_mean_5"] == 10.0
    assert featured.loc[1, "s2_mean_5"] == 15.0
    assert featured.loc[2, "s2_mean_5"] == 20.0


def test_rolling_features_do_not_mix_engine_histories():
    rows = []
    for engine_id, value in [("ENGINE-A", 10.0), ("ENGINE-B", 100.0)]:
        rows.append({
            "engine_id": engine_id, "cycle": 1,
            "setting_1": 0.0, "setting_2": 0.0, "setting_3": 0.0,
            **{f"s{i}": value if i == 2 else 1.0 for i in range(1, 22)},
        })
    featured = add_features(pd.DataFrame(rows))
    means = dict(zip(featured["engine_id"], featured["s2_mean_5"]))
    assert means == {"ENGINE-A": 10.0, "ENGINE-B": 100.0}
