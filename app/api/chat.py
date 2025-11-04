"""
Chat API endpoints for interacting with Gemini AI.
Supports both standard and streaming responses.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from app.models.schemas import ChatRequest, ChatResponse, StreamChunk
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to Gemini AI and get a response.
    
    - **message**: The message to send to the AI
    - **conversation_id**: Optional conversation ID for context
    - **model**: Optional model override
    - **temperature**: Optional temperature setting (0.0 - 2.0)
    - **max_tokens**: Optional maximum tokens in response
    - **stream**: Whether to stream the response (use /chat/stream endpoint instead)
    """
    if request.stream:
        raise HTTPException(
            status_code=400,
            detail="For streaming responses, use the /chat/stream endpoint"
        )
    
    try:
        result = await gemini_service.generate_response(
            message=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Send a message to Gemini AI and get a streaming response with thinking support.
    
    Returns Server-Sent Events (SSE) with chunks of the response.
    Each event contains:
    - type: 'thought' | 'answer' | 'done' | 'error'
    - chunk: The text content
    - done: Boolean indicating if streaming is complete
    - conversation_id: The conversation identifier
    
    - **message**: The message to send to the AI
    - **conversation_id**: Optional conversation ID for context
    - **model**: Optional model override
    - **temperature**: Optional temperature setting (0.0 - 2.0)
    - **max_tokens**: Optional maximum tokens in response
    - **system_instruction**: Optional system instruction for the model
    - **thinking_budget**: Token budget for thinking (-1 for dynamic, 0 to disable, or specific number)
    - **include_thoughts**: Whether to include thought summaries in response
    """
    async def event_generator():
        """Generate Server-Sent Events for streaming."""
        try:
            async for chunk_data in gemini_service.generate_stream_response(
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_instruction=request.system_instruction,
                thinking_budget=request.thinking_budget,
                include_thoughts=request.include_thoughts,
                conversation_id=request.conversation_id
            ):
                # Format as SSE
                chunk_json = json.dumps(chunk_data, ensure_ascii=False)
                yield f"data: {chunk_json}\n\n"
                
                # Break if done
                if chunk_data.get("done", False):
                    break
                    
        except Exception as e:
            error_data = {
                "type": "error",
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
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )


@router.get("/health")
async def chat_health():
    """Check if the chat service is healthy and can connect to Gemini API."""
    is_healthy = await gemini_service.check_health()
    
    if not is_healthy:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to Gemini API"
        )
    
    return {
        "status": "healthy",
        "service": "chat",
        "gemini_connected": True
    }
