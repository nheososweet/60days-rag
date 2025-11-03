"""
RAG API endpoints for document ingestion and querying.
Supports retrieval-augmented generation with vector databases.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from app.models.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    DocumentUploadResponse
)
from app.services.rag_service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Query the RAG system to get answers based on your knowledge base.
    
    - **query**: The question or query to ask
    - **top_k**: Number of relevant documents to retrieve (1-20)
    - **collection_name**: Optional specific collection to search in
    - **filter_metadata**: Optional metadata filters for retrieval
    - **stream**: Whether to stream the response (use /rag/query/stream endpoint instead)
    """
    if request.stream:
        raise HTTPException(
            status_code=400,
            detail="For streaming responses, use the /rag/query/stream endpoint"
        )
    
    try:
        result = await rag_service.query_rag(
            query=request.query,
            top_k=request.top_k,
            collection_name=request.collection_name,
            filter_metadata=request.filter_metadata
        )
        
        return RAGQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_rag_stream(request: RAGQueryRequest):
    """
    Query the RAG system with streaming response.
    
    Returns Server-Sent Events (SSE) with chunks of the answer.
    Each event contains a JSON object with 'chunk', 'done', and other fields.
    
    - **query**: The question or query to ask
    - **top_k**: Number of relevant documents to retrieve (1-20)
    - **collection_name**: Optional specific collection to search in
    - **filter_metadata**: Optional metadata filters for retrieval
    """
    async def event_generator():
        """Generate Server-Sent Events for streaming."""
        try:
            async for chunk_data in rag_service.query_rag_stream(
                query=request.query,
                top_k=request.top_k,
                collection_name=request.collection_name,
                filter_metadata=request.filter_metadata
            ):
                # Format as SSE
                chunk_json = json.dumps(chunk_data)
                yield f"data: {chunk_json}\n\n"
                
                # Break if done
                if chunk_data.get("done", False):
                    break
                    
        except Exception as e:
            error_data = {
                "chunk": "",
                "done": True,
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_name: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload a document to the RAG knowledge base.
    
    - **file**: The document file to upload (PDF, TXT, DOCX, etc.)
    - **collection_name**: Collection to store the document in
    - **metadata**: Optional JSON string with additional metadata
    
    Note: This endpoint is a placeholder. Full implementation requires
    document parsing, chunking, and vector embedding.
    """
    try:
        # Read file content
        content = await file.read()
        content_text = content.decode('utf-8') if file.content_type == 'text/plain' else ""
        
        # Parse metadata if provided
        metadata_dict = json.loads(metadata) if metadata else {}
        metadata_dict['filename'] = file.filename
        metadata_dict['content_type'] = file.content_type
        
        # Ingest document
        result = await rag_service.ingest_document(
            content=content_text,
            collection_name=collection_name,
            metadata=metadata_dict
        )
        
        return DocumentUploadResponse(**result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def list_collections():
    """
    List all available collections in the vector database.
    
    Returns a list of collection names that can be queried.
    """
    try:
        collections = rag_service.list_collections()
        return {
            "collections": collections,
            "count": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    Delete a collection from the vector database.
    
    - **collection_name**: Name of the collection to delete
    
    Warning: This action is irreversible.
    """
    try:
        success = rag_service.delete_collection(collection_name)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' not found"
            )
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
