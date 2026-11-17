"""API routers package."""

from fastapi import APIRouter

from app.api.analyze import router as analyze_router
from app.api.auth import router as auth_router
from app.api.enhance import router as enhance_router
from app.api.resumes import router as resumes_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(resumes_router)
api_router.include_router(analyze_router)
api_router.include_router(enhance_router)

__all__ = ["api_router"]
