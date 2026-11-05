from app.services.risk import classify_risk


def test_risk_thresholds_are_explicit():
    assert classify_risk(10) == "critical"
    assert classify_risk(20) == "critical"
    assert classify_risk(21) == "watch"
    assert classify_risk(50) == "watch"
    assert classify_risk(51) == "healthy"
