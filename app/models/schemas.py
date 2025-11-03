"""Pydantic models for API requests and responses."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message to send to the LLM")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for maintaining context")
    model: Optional[str] = Field(None, description="Model to use (defaults to config setting)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens in response")
    stream: bool = Field(False, description="Enable streaming response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Explain what is RAG in AI?",
                "stream": True,
                "temperature": 0.7
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="LLM response")
    conversation_id: str = Field(..., description="Conversation ID")
    model: str = Field(..., description="Model used for generation")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "RAG stands for Retrieval-Augmented Generation...",
                "conversation_id": "conv_123456",
                "model": "gemini-2.5-flash",
                "usage": {"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60}
            }
        }


class StreamChunk(BaseModel):
    """Model for streaming response chunks."""
    chunk: str = Field(..., description="Chunk of text")
    done: bool = Field(False, description="Whether streaming is complete")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class RAGQueryRequest(BaseModel):
    """Request model for RAG query endpoint."""
    query: str = Field(..., description="Query to search in the knowledge base")
    top_k: int = Field(5, ge=1, le=20, description="Number of relevant documents to retrieve")
    collection_name: Optional[str] = Field(None, description="Specific collection to search in")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters for retrieval")
    stream: bool = Field(False, description="Enable streaming response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the benefits of using RAG?",
                "top_k": 5,
                "stream": True
            }
        }


class RAGQueryResponse(BaseModel):
    """Response model for RAG query endpoint."""
    answer: str = Field(..., description="Generated answer based on retrieved context")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used for generation")
    query: str = Field(..., description="Original query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "RAG provides several benefits including...",
                "sources": [
                    {"content": "RAG improves accuracy...", "metadata": {"source": "doc1.pdf", "page": 1}}
                ],
                "query": "What are the benefits of using RAG?"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    collection_name: str = Field(..., description="Collection to store the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the document")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    success: bool = Field(..., description="Whether upload was successful")
    document_id: str = Field(..., description="Unique ID for the uploaded document")
    message: str = Field(..., description="Status message")
    chunks_created: int = Field(..., description="Number of chunks created from the document")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    gemini_api_connected: bool = Field(..., description="Whether Gemini API is accessible")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "gemini_api_connected": True
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
