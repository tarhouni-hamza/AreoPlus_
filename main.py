from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.routers import dashboard, engines, health

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AeroPulse API",
    description="Predictive maintenance intelligence for simulated turbofan engine data.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(engines.router)
