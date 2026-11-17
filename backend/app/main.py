"""FastAPI Main Application Entry Point."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.database import engine, Base

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("getshortlisted")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown routines."""
    logger.info("Initializing GetShortlisted API backend...")
    # Auto-create tables in development / Neon if not present
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema verified and initialized.")
    except Exception as e:
        logger.warning(f"Database connection note (will retry per request): {e}")

    yield
    logger.info("Shutting down GetShortlisted backend...")


app = FastAPI(
    title="GetShortlisted API",
    description="AI Resume Coach & Job-Fit Analyzer for Students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev & cloud deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes under /api
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker & Render deployment monitoring."""
    return {
        "status": "healthy",
        "service": "GetShortlisted API",
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    """API index."""
    return {
        "message": "Welcome to GetShortlisted API. Visit /docs for the interactive Swagger documentation.",
        "docs": "/docs",
    }
