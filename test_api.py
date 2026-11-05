from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Engine, EngineObservation


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=TEST_ENGINE)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestSession()
    db.add(Engine(
        engine_id="TEST-001", last_cycle=85, predicted_rul=12.5,
        risk_level="critical", model_version="test-model",
        updated_at=datetime.now(timezone.utc),
    ))
    db.add(EngineObservation(
        engine_id="TEST-001", cycle=85, settings={"setting_1": 0.1},
        sensors={"s2": 642.1},
    ))
    db.commit()
    db.close()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_engine_filter_and_overview():
    engines = client.get("/api/engines?risk=critical")
    overview = client.get("/api/overview")
    assert engines.status_code == 200
    assert engines.json()[0]["engine_id"] == "TEST-001"
    assert overview.json()["total_engines"] == 1
    assert overview.json()["critical_engines"] == 1


def test_missing_engine_returns_404():
    assert client.get("/api/engines/DOES-NOT-EXIST").status_code == 404


def test_engine_detail_includes_sensor_observations():
    response = client.get("/api/engines/TEST-001")
    assert response.status_code == 200
    assert response.json()["observations"][0]["sensors"]["s2"] == 642.1
