"""
VANTAGE — FastAPI Application
Main entry point with middleware, CORS, and route registration.
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes.routes import router

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("vantage_starting", version=settings.app_version)
    # Pre-load embedding model on startup to avoid cold start on first request
    try:
        from app.services.clustering.clusterer import get_embedding_model
        get_embedding_model()
        log.info("embedding_model_loaded")
    except Exception as e:
        log.warning("embedding_model_load_failed", error=str(e))
    yield
    log.info("vantage_shutdown")


app = FastAPI(
    title="VANTAGE API",
    description="AI-Powered News Intelligence & Media Bias Analysis for Nepal",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log.error("unhandled_exception", path=str(request.url), error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
