"""
Health check and system status endpoints.
"""
from fastapi import APIRouter

from app.models.schemas import HealthResponse
from app.core.config import settings
from app.services.gemini_service import gemini_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the API and its dependencies.
    
    Returns:
        - API version and status
        - Gemini API connectivity status
    """
    gemini_connected = await gemini_service.check_health()
    
    return HealthResponse(
        status="healthy" if gemini_connected else "degraded",
        version=settings.APP_VERSION,
        gemini_api_connected=gemini_connected
    )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "FastAPI + LLM + RAG + LangChain learning project",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "chat_stream": "/chat/stream",
            "rag_query": "/rag/query",
            "rag_query_stream": "/rag/query/stream",
            "upload_document": "/rag/documents/upload"
        }
    }
