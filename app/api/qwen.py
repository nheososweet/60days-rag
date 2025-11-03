"""
Qwen3 Chat API Routes - Endpoints để chat với Qwen3 local model.

Module này cung cấp các endpoints để interact với Qwen3-0.6B model
đang chạy local qua vLLM. Hoàn toàn tách biệt với Gemini endpoints.

Endpoints:
- POST /qwen/chat - Non-streaming chat
- POST /qwen/chat/stream - Streaming chat với SSE
- GET /qwen/health - Health check cho Qwen service

Design: Tách biệt hoàn toàn với Gemini để dễ maintain và compare.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from app.models.schemas import ChatRequest, ChatResponse
from app.services.qwen_service import qwen_service

# Tạo router cho Qwen endpoints
# prefix="/qwen" -> tất cả routes sẽ bắt đầu với /qwen
# tags=["Qwen Chat"] -> Nhóm endpoints trong API docs
router = APIRouter(prefix="/qwen", tags=["Qwen Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_qwen(request: ChatRequest):
    """
    Chat với Qwen3 model (NON-STREAMING mode).
    
    Endpoint này gửi message tới Qwen3 và đợi full response
    trước khi trả về. Phù hợp cho:
    - Simple Q&A
    - Quick queries
    - Khi không cần real-time response
    
    **Request Body:**
    ```json
    {
        "message": "What is FastAPI?",
        "temperature": 0.7,
        "max_tokens": 1000,
        "system_prompt": "You are a helpful assistant"
    }
    ```
    
    **Response:**
    ```json
    {
        "response": "FastAPI is a modern web framework...",
        "conversation_id": "qwen_conv_abc123",
        "model": "Qwen/Qwen3-0.6B",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 50,
            "total_tokens": 60
        }
    }
    ```
    
    **Use Cases:**
    - Code generation: "Write a Python function to..."
    - Q&A: "Explain what is RAG?"
    - Summarization: "Summarize this text: ..."
    - Translation: "Translate to Vietnamese: ..."
    
    Args:
        request: ChatRequest object chứa message và config
        
    Returns:
        ChatResponse với full answer từ Qwen3
        
    Raises:
        HTTPException: 
            - 400: Invalid request
            - 500: Server error hoặc Qwen service error
            - 503: Qwen service không available
    """
    try:
        # Log để debug (trong production nên dùng proper logger)
        print(f"[Qwen Chat] Received message: {request.message[:50]}...")
        
        # Gọi qwen_service để generate response
        # Pass tất cả parameters từ request
        result = await qwen_service.generate_response(
            message=request.message,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            conversation_id=request.conversation_id,
            system_prompt=request.system_prompt,
            context=request.context,
            enable_thinking=request.enable_thinking or False
        )
        
        # Convert result thành ChatResponse format
        # ChatResponse là Pydantic model đã định nghĩa
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            model=result["model"],
            usage=result.get("usage")  # Optional field
        )
        
    except Exception as e:
        # Catch mọi error và convert thành HTTP error
        print(f"[Qwen Chat Error] {str(e)}")
        
        # Trả về 500 Internal Server Error
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Qwen chat request: {str(e)}"
        )


@router.post("/chat/stream")
async def stream_chat_with_qwen(request: ChatRequest):
    """
    Chat với Qwen3 với STREAMING response (Server-Sent Events).
    
    Endpoint này stream response từng chunk, cho phép user
    thấy text được generate real-time. Giống như ChatGPT!
    
    **Response Format: Server-Sent Events (SSE)**
    
    SSE là protocol để server push data tới client real-time.
    Format: mỗi message là "data: <json>\\n\\n"
    
    **Example Stream:**
    ```
    data: {"chunk": "Fast", "done": false, "conversation_id": "qwen_conv_123"}
    
    data: {"chunk": "API", "done": false, "conversation_id": "qwen_conv_123"}
    
    data: {"chunk": " is", "done": false, "conversation_id": "qwen_conv_123"}
    
    data: {"chunk": "", "done": true, "conversation_id": "qwen_conv_123"}
    ```
    
    **Client-side JavaScript Example:**
    ```javascript
    const response = await fetch('/qwen/chat/stream', {
        method: 'POST',
        body: JSON.stringify({message: "Hi"})
    });
    
    const reader = response.body.getReader();
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        console.log(text);  // Print each chunk
    }
    ```
    
    **Python Client Example:**
    ```python
    import requests
    response = requests.post(
        'http://localhost:8000/qwen/chat/stream',
        json={'message': 'Hi'},
        stream=True
    )
    for line in response.iter_lines():
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            if not data['done']:
                print(data['chunk'], end='', flush=True)
    ```
    
    **Benefits của Streaming:**
    - ✅ Better UX - User thấy response ngay
    - ✅ Perceived performance - Cảm giác nhanh hơn
    - ✅ Can cancel mid-stream - Tiết kiệm resources
    - ✅ Progressive rendering - Hiển thị từng phần
    
    Args:
        request: ChatRequest object
        
    Returns:
        StreamingResponse với media_type="text/event-stream"
        
    Raises:
        HTTPException: Nếu có lỗi setup streaming
    """
    try:
        print(f"[Qwen Streaming] Starting stream for: {request.message[:50]}...")
        
        # Định nghĩa async generator để yield SSE events
        async def event_generator():
            """
            Generator function để tạo SSE events.
            
            Yield format: "data: {json}\\n\\n"
            Đây là format chuẩn của Server-Sent Events.
            """
            try:
                # Iterate qua streaming response từ qwen_service
                async for chunk_data in qwen_service.generate_stream_response(
                    message=request.message,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    conversation_id=request.conversation_id,
                    system_prompt=request.system_prompt,
                    context=request.context,
                    enable_thinking=request.enable_thinking or False
                ):
                    # Convert chunk_data thành JSON string
                    chunk_json = json.dumps(chunk_data)
                    
                    # Format theo SSE protocol
                    # "data: " prefix + JSON + "\n\n" suffix
                    yield f"data: {chunk_json}\n\n"
                    
                    # Nếu done=True, dừng streaming
                    if chunk_data.get("done", False):
                        break
                
            except Exception as e:
                # Nếu có error trong quá trình streaming
                # Gửi error message trong stream format
                error_chunk = {
                    "chunk": f"Error: {str(e)}",
                    "done": True,
                    "error": True
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        # Trả về StreamingResponse
        # media_type="text/event-stream" báo cho client đây là SSE
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                # Cache-Control: no-cache - Không cache stream
                "Cache-Control": "no-cache",
                # Connection: keep-alive - Giữ connection mở
                "Connection": "keep-alive",
                # X-Accel-Buffering: no - Disable nginx buffering (nếu có)
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        print(f"[Qwen Streaming Error] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error setting up Qwen stream: {str(e)}"
        )


@router.get("/health")
async def qwen_health_check():
    """
    Health check endpoint cho Qwen service.
    
    Endpoint này kiểm tra xem:
    1. Qwen vLLM server có đang chạy không?
    2. API có accessible không?
    3. Model có ready để serve không?
    
    **Success Response (200):**
    ```json
    {
        "status": "healthy",
        "service": "qwen-vllm",
        "model": "Qwen/Qwen3-0.6B",
        "server_url": "http://localhost:8000"
    }
    ```
    
    **Error Response (503):**
    ```json
    {
        "detail": "Qwen vLLM server is not accessible. Please check if vLLM is running."
    }
    ```
    
    **Troubleshooting khi unhealthy:**
    1. Check vLLM server có chạy không:
       ```bash
       # Windows PowerShell
       curl http://localhost:8000/v1/models
       ```
    
    2. Check process:
       ```bash
       # Windows
       tasklist | findstr python
       
       # Linux/Mac
       ps aux | grep vllm
       ```
    
    3. Restart vLLM:
       ```bash
       vllm serve Qwen/Qwen3-0.6B --port 8000
       ```
    
    Returns:
        Success message nếu healthy
        
    Raises:
        HTTPException 503: Nếu service không accessible
    """
    # Gọi health check method của qwen_service
    is_healthy = await qwen_service.check_health()
    
    if is_healthy:
        # Service đang hoạt động tốt
        return {
            "status": "healthy",
            "service": "qwen-vllm",
            "model": qwen_service.model_name,
            "server_url": qwen_service.base_url,
            "message": "Qwen service is running and ready to serve requests"
        }
    else:
        # Service không accessible
        # Trả về 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail=(
                "Qwen vLLM server is not accessible. "
                "Please check if vLLM is running on port 8000. "
                f"Expected URL: {qwen_service.base_url}"
            )
        )


@router.get("/info")
async def qwen_info():
    """
    Thông tin về Qwen model và configuration.
    
    Endpoint này trả về static info về model,
    không cần gọi vLLM server.
    
    **Response:**
    ```json
    {
        "model_name": "Qwen/Qwen3-0.6B",
        "model_size": "600M parameters",
        "context_length": "32,768 tokens",
        "server_url": "http://localhost:8000",
        "features": [
            "Multilingual support",
            "Function calling",
            "Long context (32K tokens)",
            "Fast inference with vLLM"
        ],
        "use_cases": [
            "Q&A and chat",
            "Code generation",
            "Text summarization",
            "RAG applications",
            "Local/private inference"
        ]
    }
    ```
    
    Returns:
        Model information và capabilities
    """
    return {
        "model_name": qwen_service.model_name,
        "model_size": "600M parameters",
        "context_length": "32,768 tokens",
        "server_url": qwen_service.base_url,
        "api_format": "OpenAI-compatible",
        "features": [
            "Multilingual support (English, Chinese, Vietnamese, etc.)",
            "Function calling capability",
            "Long context window (32K tokens)",
            "Fast inference with vLLM optimization",
            "Streaming support",
            "Local inference (privacy-friendly)"
        ],
        "use_cases": [
            "Q&A and conversational chat",
            "Code generation and explanation",
            "Text summarization and analysis",
            "RAG (Retrieval-Augmented Generation)",
            "Local/private LLM inference",
            "Educational purposes"
        ],
        "advantages": [
            "Small size - runs on CPU",
            "Fast inference",
            "No API costs",
            "Data privacy (local)",
            "Good for learning RAG"
        ],
        "endpoints": {
            "chat": "/qwen/chat",
            "stream": "/qwen/chat/stream",
            "health": "/qwen/health",
            "info": "/qwen/info"
        }
    }
