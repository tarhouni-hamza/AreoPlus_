from app.config import RISK_CRITICAL_CYCLES, RISK_WATCH_CYCLES


def classify_risk(predicted_rul: float) -> str:
    """Classify an engine using transparent, configurable cycle thresholds."""
    if predicted_rul <= RISK_CRITICAL_CYCLES:
        return "critical"
    if predicted_rul <= RISK_WATCH_CYCLES:
        return "watch"
    return "healthy"
