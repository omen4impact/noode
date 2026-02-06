"""FastAPI server for Noode."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from noode.api.routes import router
from noode.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(level="INFO", json_format=False)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Noode API",
    description="Autonomous AI Development Platform API",
    version="0.5.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint redirects to API docs."""
    return {
        "message": "Noode API",
        "version": "0.5.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
