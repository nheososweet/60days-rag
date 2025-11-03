# 🚀 Quick Start Guide - Qwen3 Integration

## ✅ Bạn đã hoàn thành tích hợp Qwen3!

### 📁 Files đã tạo:

```
app/
├── services/
│   └── qwen_service.py        ✅ Service giao tiếp với vLLM
├── api/
│   └── qwen.py                ✅ API routes cho Qwen
└── core/
    └── config.py              ✅ Config đã update

test_qwen.py                   ✅ Test script
```

---

## 🎯 Cách sử dụng

### Bước 1: Đảm bảo vLLM đang chạy

```powershell
# Kiểm tra vLLM có chạy không
curl http://localhost:8000/v1/models
```

Nếu chưa chạy, start vLLM:

```powershell
vllm serve Qwen/Qwen3-0.6B --port 8000
```

### Bước 2: Khởi động FastAPI

```powershell
# Nếu chưa chạy
python main.py

# Hoặc
uvicorn main:app --reload
```

### Bước 3: Test Qwen Endpoints

#### **Option 1: Dùng test script (Recommended)**

```powershell
python test_qwen.py
```

Test script sẽ chạy:

- ✓ Health check
- ✓ Model info
- ✓ Non-streaming chat
- ✓ Streaming chat
- ✓ Custom system prompts

#### **Option 2: Dùng Interactive API Docs**

Mở browser: http://localhost:8000/docs

Bạn sẽ thấy group mới: **"Qwen Chat"** với 4 endpoints:

- `GET /qwen/health` - Health check
- `GET /qwen/info` - Model information
- `POST /qwen/chat` - Non-streaming chat
- `POST /qwen/chat/stream` - Streaming chat

#### **Option 3: Dùng curl**

```powershell
# 1. Health check
curl http://localhost:8000/qwen/health

# 2. Model info
curl http://localhost:8000/qwen/info

# 3. Simple chat
curl -X POST "http://localhost:8000/qwen/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What is RAG in AI?\"}"

# 4. Chat with system prompt
curl -X POST "http://localhost:8000/qwen/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Write a hello world in Python\", \"system_prompt\": \"You are a Python expert\"}"
```

#### **Option 4: Dùng Python requests**

```python
import requests

# Simple chat
response = requests.post(
    "http://localhost:8000/qwen/chat",
    json={
        "message": "Explain FastAPI briefly",
        "temperature": 0.7
    }
)

print(response.json()["response"])
```

---

## 📖 API Endpoints Chi Tiết

### 1. `GET /qwen/health`

**Mục đích:** Kiểm tra Qwen service có hoạt động không

**Response:**

```json
{
  "status": "healthy",
  "service": "qwen-vllm",
  "model": "Qwen/Qwen3-0.6B",
  "server_url": "http://localhost:8000"
}
```

### 2. `GET /qwen/info`

**Mục đích:** Lấy thông tin về Qwen model

**Response:**

```json
{
  "model_name": "Qwen/Qwen3-0.6B",
  "model_size": "600M parameters",
  "context_length": "32,768 tokens",
  "features": [...],
  "use_cases": [...]
}
```

### 3. `POST /qwen/chat`

**Mục đích:** Chat non-streaming với Qwen3

**Request:**

```json
{
  "message": "What is FastAPI?",
  "temperature": 0.7, // Optional: 0.0-2.0
  "max_tokens": 1000, // Optional
  "system_prompt": "You are..." // Optional
}
```

**Response:**

```json
{
  "response": "FastAPI is a modern...",
  "conversation_id": "qwen_conv_abc123",
  "model": "Qwen/Qwen3-0.6B",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### 4. `POST /qwen/chat/stream`

**Mục đích:** Chat với streaming response (real-time)

**Request:** Giống như `/qwen/chat`

**Response:** Server-Sent Events (SSE)

```
data: {"chunk": "Fast", "done": false, "conversation_id": "..."}

data: {"chunk": "API", "done": false, "conversation_id": "..."}

data: {"chunk": "", "done": true, "conversation_id": "..."}
```

---

## 💡 Use Cases & Examples

### 1. Simple Q&A

```json
{
  "message": "What is RAG in AI?",
  "temperature": 0.7
}
```

### 2. Code Generation

```json
{
  "message": "Write a Python function to calculate fibonacci",
  "system_prompt": "You are an expert Python programmer",
  "temperature": 0.3
}
```

### 3. Text Summarization

```json
{
  "message": "Summarize this text: [long text here]",
  "temperature": 0.5,
  "max_tokens": 500
}
```

### 4. Translation

```json
{
  "message": "Translate to Vietnamese: Hello, how are you?",
  "system_prompt": "You are a professional translator",
  "temperature": 0.3
}
```

### 5. Creative Writing

```json
{
  "message": "Write a short story about AI",
  "system_prompt": "You are a creative writer",
  "temperature": 1.5
}
```

---

## 🔧 Troubleshooting

### ❌ Error: "Qwen vLLM server is not accessible"

**Solutions:**

1. Check vLLM có chạy không:

   ```powershell
   curl http://localhost:8000/v1/models
   ```

2. Start vLLM nếu chưa chạy:

   ```powershell
   vllm serve Qwen/Qwen3-0.6B --port 8000
   ```

3. Check port conflict (port 8000 bị chiếm):
   ```powershell
   netstat -ano | findstr :8000
   ```

### ❌ Error: "Connection refused"

**Solutions:**

1. Đảm bảo FastAPI đang chạy:

   ```powershell
   python main.py
   ```

2. Check đúng port chưa (FastAPI default: 8000, nhưng có thể đổi trong .env)

### ❌ Response quá chậm

**Solutions:**

1. Giảm `max_tokens` xuống (vd: 500)
2. Tăng timeout trong config
3. Check CPU/Memory usage
4. Nếu có GPU, đảm bảo vLLM đang dùng GPU

### ❌ Response không đúng ý

**Solutions:**

1. Thử thay đổi `temperature`:
   - Thấp hơn (0.3) = deterministic
   - Cao hơn (1.5) = creative
2. Thử thêm `system_prompt` cụ thể hơn
3. Refine câu hỏi rõ ràng hơn

---

## 📊 So sánh Gemini vs Qwen3

| Feature      | Gemini (Cloud)      | Qwen3 (Local)         |
| ------------ | ------------------- | --------------------- |
| **Location** | Cloud API           | Local (vLLM)          |
| **Size**     | Large (billions)    | 600M params           |
| **Speed**    | Fast (Google infra) | Depends on hardware   |
| **Cost**     | API quota/paid      | Free (after download) |
| **Privacy**  | Data sent to Google | 100% local, private   |
| **Internet** | Required            | Not required          |
| **Context**  | 1M tokens           | 32K tokens            |
| **Quality**  | Excellent           | Good for size         |
| **Use Case** | Production          | Learning, RAG, local  |

---

## 🎓 Bước tiếp theo

### ✅ Hoàn thành:

- [x] Qwen3 service
- [x] API endpoints
- [x] Streaming support
- [x] Health checks
- [x] Test script

### 📅 Tiếp theo học:

1. **Vector Databases** (Week 3-4)

   - ChromaDB integration
   - Document embeddings
   - Semantic search

2. **RAG với Qwen3** (Week 5-6)

   - Document ingestion
   - Retrieval pipeline
   - Context-aware generation

3. **LangChain** (Week 7-8)

   - Chains với Qwen3
   - Memory management
   - Agent creation

4. **Advanced RAG** (Week 9-12)
   - Agentic RAG
   - LangGraph workflows
   - Multi-agent systems

---

## 📝 Notes

### Qwen3 advantages cho learning:

1. ✅ **Local = Privacy** - Không lo data leak
2. ✅ **Free** - Không tốn API cost
3. ✅ **Fast iteration** - Test nhanh, không limit
4. ✅ **Good for RAG** - Context window 32K tokens
5. ✅ **Educational** - Hiểu được flow của LLM

### Khi nào dùng Gemini vs Qwen3:

- **Gemini**: Production, cần quality cao, internet stable
- **Qwen3**: Learning, testing, RAG experiments, offline

---

## 🎉 Chúc mừng!

Bạn đã tích hợp thành công Qwen3-0.6B vào project!

**Next steps:**

1. Chạy `python test_qwen.py` để verify
2. Thử các use cases khác nhau
3. Compare response quality giữa Gemini và Qwen3
4. Chuẩn bị học RAG với Qwen3!

**Happy coding!** 🚀
