"""
Services module for business logic and external API interactions.

Services:
- gemini_service: Google Gemini AI (cloud-based)
- qwen_service: Qwen3-0.6B local model (via vLLM)
- rag_service: RAG operations (future)
"""
from .gemini_service import gemini_service, GeminiService
from .qwen_service import qwen_service, QwenService
from .rag_service import rag_service, RAGService

__all__ = [
    # Gemini AI (cloud)
    "gemini_service",
    "GeminiService",
    # Qwen3 (local)
    "qwen_service",
    "QwenService",
    # RAG
    "rag_service",
    "RAGService"
]
