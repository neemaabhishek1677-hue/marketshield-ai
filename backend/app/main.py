from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.database import Base, engine, AsyncSessionLocal

settings = get_settings()
scheduler = None  # Lazy initialization


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scheduler
    from app.services.scheduler_service import IngestionScheduler
    
    if settings.is_sqlite:
        Path("data").mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize and start scheduler
    scheduler = IngestionScheduler()
    await scheduler.initialize(AsyncSessionLocal)
    
    yield
    
    # Shutdown
    if scheduler:
        await scheduler.shutdown()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="AI-Based Market Manipulation & Insider Trading Detection Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "product": "MarketShield AI",
        "docs": "/docs",
        "api": "/api/v1",
        "disclaimer": "Market surveillance platform with real market data and simulated entity layer — not legal or investment advice.",
    }
