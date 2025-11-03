# 📘 Giải thích Chi tiết - Qwen3 Integration

## 🎯 Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────────┐
│                       USER/CLIENT                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application (Port 8000)                │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API Layer: app/api/qwen.py                        │     │
│  │  - POST /qwen/chat (non-streaming)                 │     │
│  │  - POST /qwen/chat/stream (streaming SSE)          │     │
│  │  - GET /qwen/health                                │     │
│  │  - GET /qwen/info                                  │     │
│  └────────────────────────────────────────────────────┘     │
                            ↓
│  ┌────────────────────────────────────────────────────┐     │
│  │  Service Layer: app/services/qwen_service.py       │     │
│  │  - generate_response() → Non-streaming             │     │
│  │  - generate_stream_response() → Streaming          │     │
│  │  - check_health() → Health check                   │     │
│  └────────────────────────────────────────────────────┘     │
                            ↓
│  ┌────────────────────────────────────────────────────┐     │
│  │  HTTP Client (httpx AsyncClient)                   │     │
│  │  - Gọi vLLM API                                    │     │
│  │  - Handle streaming/non-streaming                  │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              vLLM Server (Port 8000)                        │
│  - OpenAI-compatible API                                    │
│  - Endpoint: /v1/chat/completions                          │
│  - Qwen3-0.6B model loaded in memory                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Files Created - Chi tiết từng file

### 1. `app/core/config.py` (Updated)

**Vai trò:** Quản lý configuration

**Thêm mới:**

```python
QWEN_BASE_URL: str = "http://localhost:8000"  # vLLM server URL
QWEN_MODEL: str = "Qwen/Qwen3-0.6B"          # Model name
QWEN_TIMEOUT: int = 120                       # Request timeout
```

**Giải thích:**

- `QWEN_BASE_URL`: Địa chỉ của vLLM server (KHÁC với FastAPI port!)
- `QWEN_MODEL`: Tên model để display và verify
- `QWEN_TIMEOUT`: Timeout cho HTTP requests (120s vì inference có thể lâu)

**Environment Variables (.env):**

```env
QWEN_BASE_URL=http://localhost:8000
QWEN_MODEL=Qwen/Qwen3-0.6B
QWEN_TIMEOUT=120
```

---

### 2. `app/services/qwen_service.py` (New)

**Vai trò:** Business logic layer - Giao tiếp với vLLM

#### **Class: QwenService**

##### **Method: `__init__()`**

```python
def __init__(self):
    self.base_url = settings.QWEN_BASE_URL
    self.model_name = settings.QWEN_MODEL
    self.client = httpx.AsyncClient(timeout=settings.QWEN_TIMEOUT)
```

**Giải thích:**

- Load config từ settings
- Tạo async HTTP client với timeout
- Client này sẽ reuse connections (efficient!)

##### **Method: `generate_response()` - NON-STREAMING**

**Flow:**

```
1. Chuẩn bị messages (system + user)
   ↓
2. Tạo payload theo OpenAI format
   ↓
3. POST tới /v1/chat/completions với stream=False
   ↓
4. Nhận full response
   ↓
5. Parse và return
```

**Request Format:**

```json
{
  "model": "Qwen/Qwen3-0.6B",
  "messages": [
    { "role": "system", "content": "You are..." },
    { "role": "user", "content": "Hello" }
  ],
  "temperature": 0.7,
  "max_tokens": 2048,
  "stream": false
}
```

**Response Format:**

```json
{
  "choices": [
    {
      "message": {
        "content": "Response text here..."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

**Trả về:**

```python
{
    "response": "Text response",
    "conversation_id": "qwen_conv_abc123",
    "model": "Qwen/Qwen3-0.6B",
    "usage": {...}
}
```

##### **Method: `generate_stream_response()` - STREAMING**

**Flow:**

```
1. Chuẩn bị messages
   ↓
2. POST với stream=True
   ↓
3. Nhận SSE stream
   ↓
4. Parse từng line
   ↓
5. Yield chunks
   ↓
6. Done signal
```

**SSE Format từ vLLM:**

```
data: {"choices": [{"delta": {"content": "Hello"}}]}

data: {"choices": [{"delta": {"content": " world"}}]}

data: [DONE]
```

**Yield Format cho API:**

```python
{
    "chunk": "Hello",
    "done": False,
    "conversation_id": "qwen_conv_abc123"
}
# ... more chunks ...
{
    "chunk": "",
    "done": True,
    "conversation_id": "qwen_conv_abc123"
}
```

**Tại sao dùng AsyncIterator?**

```python
async def generate_stream_response(...) -> AsyncIterator[Dict]:
    async for chunk in ...:
        yield chunk
```

- `AsyncIterator` cho phép yield từng phần data
- Không cần load hết response vào memory
- Client có thể nhận data ngay lập tức
- Efficient và scalable!

##### **Method: `check_health()`**

```python
async def check_health(self) -> bool:
    try:
        response = await self.client.get(f"{base_url}/v1/models", timeout=5.0)
        return response.status_code == 200
    except:
        return False
```

**Giải thích:**

- Gọi `/v1/models` endpoint của vLLM
- Timeout ngắn (5s) vì chỉ là health check
- Return True/False thay vì raise exception

---

### 3. `app/api/qwen.py` (New)

**Vai trò:** API endpoints - Interface với client

#### **Router Setup:**

```python
router = APIRouter(prefix="/qwen", tags=["Qwen Chat"])
```

- `prefix="/qwen"`: Tất cả routes bắt đầu với `/qwen`
- `tags=["Qwen Chat"]`: Nhóm trong API docs

#### **Endpoint: `POST /qwen/chat`**

**Request → Service → Response:**

```
ChatRequest (Pydantic)
    ↓
Validate fields
    ↓
qwen_service.generate_response()
    ↓
ChatResponse (Pydantic)
    ↓
JSON response to client
```

**Error Handling:**

```python
try:
    result = await qwen_service.generate_response(...)
    return ChatResponse(**result)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

**Giải thích:**

- Catch tất cả exceptions
- Convert thành HTTP error (500)
- Client nhận response rõ ràng thay vì connection drop

#### **Endpoint: `POST /qwen/chat/stream`**

**Streaming Flow:**

```
Client request
    ↓
Create async generator (event_generator)
    ↓
Generator calls qwen_service.generate_stream_response()
    ↓
For each chunk:
    - Convert to JSON
    - Format as SSE: "data: {json}\n\n"
    - Yield to client
    ↓
StreamingResponse sends chunks to client
```

**SSE Protocol:**

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"chunk": "Hello", "done": false}

data: {"chunk": " world", "done": false}

data: {"chunk": "", "done": true}
```

**Tại sao dùng async generator?**

```python
async def event_generator():
    async for chunk in qwen_service.generate_stream_response(...):
        yield f"data: {json.dumps(chunk)}\n\n"
```

- Generator tạo data on-demand
- Không block thread
- Memory efficient
- Perfect cho streaming!

#### **Endpoint: `GET /qwen/health`**

**Simple check:**

```python
is_healthy = await qwen_service.check_health()
if is_healthy:
    return {"status": "healthy", ...}
else:
    raise HTTPException(status_code=503, detail="...")
```

**HTTP Status Codes:**

- `200 OK`: Service healthy
- `503 Service Unavailable`: vLLM không accessible

---

### 4. `main.py` (Updated)

**Import Qwen router:**

```python
from app.api.qwen import router as qwen_router
```

**Include router:**

```python
app.include_router(qwen_router)
```

**Order matters:**

```python
app.include_router(health_router)  # Root và health
app.include_router(chat_router)    # Gemini (/chat)
app.include_router(qwen_router)    # Qwen (/qwen)
app.include_router(rag_router)     # RAG (/rag)
```

**Giải thích:**

- Health check đầu tiên (most basic)
- Gemini và Qwen tách biệt
- RAG cuối cùng (sẽ dùng cả Gemini và Qwen)

---

### 5. `test_qwen.py` (New)

**Test Suite Structure:**

```python
1. test_health_check()           # Basic connectivity
2. test_model_info()             # Static info
3. test_non_streaming_chat()     # Core functionality
4. test_streaming_chat()         # Streaming functionality
5. test_with_system_prompt()     # Advanced features
```

**Tại sao test theo thứ tự này?**

1. Health check trước → Fail fast nếu server không chạy
2. Model info → Static endpoint, không cần vLLM
3. Non-streaming → Đơn giản nhất
4. Streaming → Phức tạp hơn
5. System prompts → Advanced use case

---

## 🔄 Data Flow Examples

### Example 1: Non-Streaming Chat

```
┌─────────┐
│ Client  │
└────┬────┘
     │ POST /qwen/chat
     │ {"message": "Hello"}
     ↓
┌─────────────────┐
│ qwen.py         │
│ @router.post    │
└────┬────────────┘
     │ await qwen_service.generate_response(...)
     ↓
┌──────────────────┐
│ qwen_service.py  │
│ generate_response│
└────┬─────────────┘
     │ POST http://localhost:8000/v1/chat/completions
     │ {"model": "...", "messages": [...], "stream": false}
     ↓
┌─────────────┐
│ vLLM Server │
└────┬────────┘
     │ {"choices": [{"message": {"content": "Hi!"}}]}
     ↓
┌──────────────────┐
│ qwen_service.py  │
│ Parse response   │
└────┬─────────────┘
     │ {"response": "Hi!", "conversation_id": "..."}
     ↓
┌─────────────────┐
│ qwen.py         │
│ ChatResponse    │
└────┬────────────┘
     │ JSON
     ↓
┌─────────┐
│ Client  │ Receives: {"response": "Hi!", ...}
└─────────┘
```

### Example 2: Streaming Chat

```
Client                  API                 Service              vLLM
  │                      │                     │                   │
  │ POST /qwen/stream    │                     │                   │
  │─────────────────────>│                     │                   │
  │                      │ call generator      │                   │
  │                      │────────────────────>│                   │
  │                      │                     │ POST stream=true  │
  │                      │                     │──────────────────>│
  │                      │                     │                   │
  │                      │                     │<──────────────────│
  │                      │                     │ SSE chunk 1       │
  │                      │<────────────────────│                   │
  │<─────────────────────│ "data: {...}\n\n"  │                   │
  │ Chunk 1              │                     │                   │
  │                      │                     │<──────────────────│
  │                      │                     │ SSE chunk 2       │
  │                      │<────────────────────│                   │
  │<─────────────────────│ "data: {...}\n\n"  │                   │
  │ Chunk 2              │                     │                   │
  │                      │                     │                   │
  │ ...                  │ ...                 │ ...               │
  │                      │                     │                   │
  │                      │                     │<──────────────────│
  │                      │                     │ [DONE]            │
  │                      │<────────────────────│                   │
  │<─────────────────────│ "data: {done:true}"│                   │
  │ Done!                │                     │                   │
```

---

## 🎓 Key Concepts Explained

### 1. **Async/Await**

```python
async def generate_response(...):  # async function
    response = await self.client.post(...)  # await = chờ không block
    return result
```

**Tại sao dùng async?**

- Không block thread khi chờ I/O
- Có thể handle nhiều requests cùng lúc
- Better performance và scalability

### 2. **AsyncIterator và Yield**

```python
async def generate_stream_response(...) -> AsyncIterator[Dict]:
    async for chunk in stream:
        yield {"chunk": chunk}  # Yield = trả về từng phần
```

**Iterator vs Regular Function:**

```python
# Regular function - return all at once
def get_numbers():
    return [1, 2, 3, 4, 5]

# Iterator - yield one by one
def generate_numbers():
    for i in range(1, 6):
        yield i
```

### 3. **Server-Sent Events (SSE)**

**Format:**

```
data: <json>\n\n
```

**Example:**

```
data: {"chunk": "Hello"}

data: {"chunk": " world"}

data: [DONE]
```

**Client consumption:**

```javascript
// JavaScript
const eventSource = new EventSource("/qwen/chat/stream");
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.chunk);
};
```

```python
# Python
response = requests.post(..., stream=True)
for line in response.iter_lines():
    if line.startswith(b'data: '):
        data = json.loads(line[6:])
        print(data['chunk'], end='')
```

### 4. **Context Manager (async with)**

```python
async with self.client.stream(...) as response:
    async for line in response.aiter_lines():
        # Process line
```

**Giải thích:**

- `async with` đảm bảo connection được close sau khi done
- Tự động cleanup resources
- Exception safe

### 5. **Error Handling Layers**

```
Layer 1: Service Layer
├─ Try/catch HTTP errors
└─ Convert to Python exceptions

Layer 2: API Layer
├─ Try/catch service exceptions
└─ Convert to HTTPException

Layer 3: FastAPI
├─ Catch HTTPException
└─ Return JSON error response

Layer 4: Global Handler
├─ Catch unhandled exceptions
└─ Return 500 error
```

---

## 💡 Best Practices Applied

### 1. **Separation of Concerns**

```
API Layer (qwen.py)
├─ Handle HTTP requests/responses
├─ Validation (Pydantic)
└─ Error formatting

Service Layer (qwen_service.py)
├─ Business logic
├─ External API calls
└─ Data transformation
```

### 2. **Type Hints**

```python
async def generate_response(
    self,
    message: str,           # Type hint
    temperature: Optional[float] = None,
    ...
) -> Dict[str, Any]:        # Return type
```

**Benefits:**

- Better IDE autocomplete
- Type checking
- Self-documenting code

### 3. **Dependency Injection**

```python
# Service instance created once
qwen_service = QwenService()

# Router imports and uses it
from app.services.qwen_service import qwen_service

@router.post("/chat")
async def chat(...):
    result = await qwen_service.generate_response(...)
```

### 4. **Configuration Management**

```python
# Don't hardcode!
# ❌ Bad
base_url = "http://localhost:8000"

# ✅ Good
base_url = settings.QWEN_BASE_URL
```

### 5. **Comprehensive Comments**

```python
"""
Docstring explains:
- What the function does
- Args with types and descriptions
- Returns with format
- Examples
"""

# Inline comments explain WHY
# Not WHAT (code should be self-explanatory)
```

---

## 🔍 Debugging Tips

### 1. **Check Logs**

```python
print(f"[Qwen] Received: {message}")
print(f"[Qwen] Response: {result}")
```

### 2. **Test Endpoints Individually**

```bash
# Test vLLM directly
curl http://localhost:8000/v1/models

# Test FastAPI health
curl http://localhost:8000/qwen/health

# Test chat
curl -X POST http://localhost:8000/qwen/chat -d '{"message":"Hi"}'
```

### 3. **Use API Docs**

Open http://localhost:8000/docs

- Try endpoints interactively
- See request/response schemas
- Check error messages

### 4. **Monitor Resource Usage**

```powershell
# Check CPU/Memory
Get-Process python

# Check network
netstat -ano | findstr :8000
```

---

## 🎯 Next Steps

Bây giờ bạn đã có:
✅ Gemini (cloud) cho production quality
✅ Qwen3 (local) cho learning và experiments

**Tiếp theo:**

1. Test cả 2 models và compare
2. Học về embeddings và vector databases
3. Implement RAG với Qwen3
4. Add LangChain cho advanced workflows

**Happy learning!** 🚀
