"""
Main FastAPI application entry point.
Configures the app, middleware, routes, and starts the server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api import chat_router, rag_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # 60 Days RAG Learning Project
    
    A comprehensive FastAPI project for learning:
    - **FastAPI**: Modern Python web framework
    - **LLM Integration**: Google Gemini AI
    - **RAG**: Retrieval-Augmented Generation
    - **LangChain**: LLM application framework
    - **LangGraph**: Agent orchestration
    - **Vector Databases**: Semantic search and embeddings
    
    ## Features
    - ✅ Chat with Gemini AI (standard & streaming)
    - ✅ RAG query endpoints (with streaming support)
    - ⏳ Document ingestion and processing
    - ⏳ LangChain integration
    - ⏳ Agentic RAG workflows
    - ⏳ LangGraph multi-agent systems
    
    ## Getting Started
    1. Check `/health` to verify API status
    2. Use `/chat` or `/chat/stream` for AI chat
    3. Use `/rag/query` for knowledge base queries
    4. Upload documents via `/rag/documents/upload`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


# Include routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(rag_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
