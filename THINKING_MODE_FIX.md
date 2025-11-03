# 🔧 Thinking Mode Fix - Chi tiết các thay đổi

## ❌ Vấn đề ban đầu

Khi bạn call API với `enable_thinking: true`, không thấy response có thinking content:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3201/qwen/chat/stream' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "Explain what is RAG in AI?",
  "stream": true,
  "temperature": 0.7,
  "enable_thinking": true
}'
```

**Kết quả**: Chỉ thấy `type: "content"`, không có `type: "thinking"`

## 🔍 Root Cause Analysis

### 1. **ChatRequest model thiếu field `enable_thinking`**

- File: `app/models/schemas.py`
- Model chỉ có: `message`, `temperature`, `max_tokens`, `stream`, `system_prompt`
- **Thiếu**: `enable_thinking` và `context`

### 2. **API routes không pass parameter**

- File: `app/api/qwen.py`
- Cả 2 endpoints (`/chat` và `/chat/stream`) đều không pass `enable_thinking` vào service
- Service nhận `enable_thinking=False` (default value)

## ✅ Các fixes đã thực hiện

### Fix 1: Thêm fields vào ChatRequest model

**File**: `app/models/schemas.py`

```python
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(...)
    conversation_id: Optional[str] = Field(None, ...)
    model: Optional[str] = Field(None, ...)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, ...)
    max_tokens: Optional[int] = Field(None, gt=0, ...)
    stream: bool = Field(False, ...)
    system_prompt: Optional[str] = Field(None, ...)

    # ✅ ADDED: Support thinking mode
    enable_thinking: Optional[bool] = Field(
        False,
        description="Enable thinking mode - model shows reasoning process in <think> tags (Qwen only)"
    )

    # ✅ ADDED: Support RAG context injection
    context: Optional[str] = Field(
        None,
        description="Additional context to inject into prompt (used for RAG)"
    )
```

### Fix 2: Pass parameters trong non-streaming endpoint

**File**: `app/api/qwen.py` - `/qwen/chat` endpoint

```python
result = await qwen_service.generate_response(
    message=request.message,
    temperature=request.temperature,
    max_tokens=request.max_tokens,
    conversation_id=request.conversation_id,
    system_prompt=request.system_prompt,
    context=request.context,                        # ✅ ADDED
    enable_thinking=request.enable_thinking or False # ✅ ADDED
)
```

### Fix 3: Pass parameters trong streaming endpoint

**File**: `app/api/qwen.py` - `/qwen/chat/stream` endpoint

```python
async for chunk_data in qwen_service.generate_stream_response(
    message=request.message,
    temperature=request.temperature,
    max_tokens=request.max_tokens,
    conversation_id=request.conversation_id,
    system_prompt=request.system_prompt,
    context=request.context,                        # ✅ ADDED
    enable_thinking=request.enable_thinking or False # ✅ ADDED
):
    # ... yield chunks
```

## 🧪 Test Cases

### Test 1: Streaming với thinking mode

```bash
curl -X POST http://127.0.0.1:3201/qwen/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 2+2? Think step by step.",
    "temperature": 0.7,
    "enable_thinking": true,
    "system_prompt": "You are a math tutor. Show your reasoning."
  }'
```

**Expected output**:

```
data: {"type":"thinking","thinking_content":"Let me think... 2+2 means...","chunk":"","done":false}
data: {"type":"content","chunk":"The answer is 4","done":false}
data: {"chunk":"","done":true}
```

### Test 2: Non-streaming với thinking mode

```bash
curl -X POST http://127.0.0.1:3201/qwen/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 2+2? Think step by step.",
    "enable_thinking": true
  }'
```

**Expected output**:

```json
{
  "response": "The answer is 4",
  "thinking_content": "Let me think... 2+2 means adding 2 and 2...",
  "conversation_id": "qwen_conv_abc123",
  "model": "Qwen/Qwen3-0.6B",
  "enable_thinking": true,
  "usage": {...}
}
```

### Test 3: Python test scripts

```bash
# Quick test
python quick_test_thinking.py

# Comprehensive test suite
python test_thinking.py
```

## 📊 Response Format chi tiết

### Streaming Response Chunks

#### Type 1: Thinking chunk

```json
{
  "type": "thinking",
  "thinking_content": "Let me analyze this step by step...",
  "chunk": "",
  "done": false,
  "conversation_id": "qwen_conv_123"
}
```

#### Type 2: Content chunk

```json
{
  "type": "content",
  "chunk": "The answer is",
  "done": false,
  "conversation_id": "qwen_conv_123"
}
```

#### Type 3: Finish chunk

```json
{
  "type": "finish",
  "finish_reason": "stop",
  "chunk": "",
  "done": true,
  "conversation_id": "qwen_conv_123"
}
```

#### Type 4: Error chunk

```json
{
  "type": "error",
  "chunk": "Connection error: ...",
  "done": true,
  "error": true,
  "conversation_id": "qwen_conv_123"
}
```

### Non-Streaming Response

```json
{
  "response": "Final answer without <think> tags",
  "thinking_content": "Reasoning process extracted from <think> tags",
  "conversation_id": "qwen_conv_123",
  "model": "Qwen/Qwen3-0.6B",
  "enable_thinking": true,
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

## ⚠️ Important Notes về Thinking Mode

### 1. **Model behavior**

- Qwen3-0.6B **không phải lúc nào** cũng generate `<think>` tags
- Tỷ lệ xuất hiện thinking tags phụ thuộc vào:
  - Prompt quality ("Think step by step", "Show your reasoning")
  - System prompt ("You must show thinking process")
  - Temperature (thấp hơn = consistent hơn)
  - Question complexity (complex questions → more thinking)

### 2. **Better thinking support**

Models có thinking mode tốt hơn:

- **Qwen2.5-7B-Instruct**: Better reasoning, more consistent
- **QwQ-32B-Preview**: Specialized thinking model
- **Qwen2.5-14B/32B**: Advanced reasoning capabilities

### 3. **Prompt engineering tips**

```python
# ❌ Weak prompt
"What is RAG?"

# ✅ Strong prompt
"Explain what is RAG. Think carefully step by step before answering."

# ✅ Best prompt with system instruction
system_prompt = "You are an AI expert who always shows reasoning process in <think> tags before answering."
message = "Explain RAG in simple terms."
```

### 4. **Debug thinking mode**

Check if model actually generates `<think>` tags:

```python
# Enable vLLM debug logging
# Trong vLLM server, check raw output
# Nếu không có <think> trong raw output → model không generate
# Nếu có <think> nhưng không parse → bug trong parser
```

## 🚀 Next Steps

1. **Test với current model**:

   ```bash
   python quick_test_thinking.py
   ```

2. **Nếu không có thinking content**:

   - Try stronger prompts
   - Check vLLM server logs
   - Consider upgrading model

3. **Optional: Upgrade model** (nếu cần better thinking):

   ```bash
   # Stop current vLLM
   # Start with bigger model
   python -m vllm.entrypoints.openai.api_server \
     --model Qwen/Qwen2.5-7B-Instruct \
     --port 8000

   # Update config.py
   QWEN_MODEL = "Qwen/Qwen2.5-7B-Instruct"
   ```

4. **Move to RAG integration**:
   - Thinking mode sẽ rất hữu ích cho RAG
   - Có thể thấy model reasoning về retrieved context
   - Debug why model gives certain answers

## 📁 Files Changed

1. ✅ `app/models/schemas.py` - Added `enable_thinking` và `context` fields
2. ✅ `app/api/qwen.py` - Pass parameters to service (both endpoints)
3. ✅ `app/services/qwen_service.py` - Already has thinking support (unchanged)
4. ✅ `test_thinking.py` - Comprehensive test suite
5. ✅ `quick_test_thinking.py` - Quick verification script

## 🎯 Summary

**Before**: `enable_thinking: true` trong request → bị ignore → no thinking output

**After**: `enable_thinking: true` → passed to service → thinking parser activated → thinking content in response

**Result**: Thinking mode **should work** nếu model generates `<think>` tags. Nếu không thấy thinking, đó là model behavior, không phải bug.
