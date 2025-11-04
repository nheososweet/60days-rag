# RAG Query API Documentation

Hướng dẫn chi tiết về RAG (Retrieval-Augmented Generation) Query API

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Testing Guide](#testing-guide)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### RAG là gì?

**RAG (Retrieval-Augmented Generation)** là kỹ thuật kết hợp:
- **Retrieval**: Tìm kiếm thông tin từ documents
- **Augmented**: Tăng cường context cho AI
- **Generation**: AI sinh ra câu trả lời dựa trên context

### Workflow

```
User Question
    ↓
Embed Question (768d vector)
    ↓
Search Similar Chunks (Vector DB)
    ↓
Build Context (Top-K chunks)
    ↓
Create Prompt (Instructions + Context + Question)
    ↓
Call Gemini AI
    ↓
Generate Answer + Sources
```

### So sánh: Chat thuần vs RAG

| Feature | Chat Thuần | RAG |
|---------|------------|-----|
| **Knowledge** | General (training data) | Specific (your documents) |
| **Up-to-date** | ❌ Outdated | ✅ Current (your data) |
| **Hallucination** | ⚠️ Possible | ✅ Grounded in context |
| **Source** | ❌ No citations | ✅ Shows sources |
| **Use Case** | General Q&A | Domain-specific Q&A |

---

## 🏗️ Architecture

### Components

```
┌─────────────────┐
│  RAG API        │
│  (rag.py)       │
└────┬────────────┘
     │
     ├─► EmbeddingService (text-embedding-004)
     │   └─ Convert text → 768d vector
     │
     ├─► VectorDBService (ChromaDB)
     │   └─ Store & search embeddings
     │
     └─► GeminiService (gemini-2.0-flash-exp)
         └─ Generate answers from context
```

### Data Flow

```
Documents (PDF, TXT)
    ↓ (uploaded via /api/documents/upload)
Chunks (500-1000 chars)
    ↓ (embedded via text-embedding-004)
Vectors (768 dimensions)
    ↓ (stored in ChromaDB)
Ready for RAG queries!
```

---

## 🔌 API Endpoints

### 1. POST /api/rag/query

Hỏi câu hỏi dựa trên documents đã upload.

#### Request Body

```json
{
  "question": "Giyu Tomioka là ai?",
  "n_results": 5,
  "document_id": null,
  "include_context": false
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | ✅ Yes | - | Câu hỏi của user |
| `n_results` | integer | ❌ No | 5 | Số chunks muốn lấy (1-20) |
| `document_id` | string | ❌ No | null | Filter theo document cụ thể |
| `include_context` | boolean | ❌ No | false | Return context đã dùng |

**N_results Guide:**
- **1-3**: Fast, focused (có thể miss info)
- **5-10**: Balanced, recommended ✅
- **15-20**: Comprehensive (expensive, may confuse AI)

#### Response

```json
{
  "success": true,
  "question": "Giyu Tomioka là ai?",
  "answer": "Giyu Tomioka là Trụ Nước (Water Hashira) trong Sát Quỷ Đội...",
  "sources": [
    {
      "chunk_id": "chunk_123",
      "text": "Full chunk text here...",
      "text_preview": "Preview of chunk...",
      "distance": 0.234,
      "similarity": 0.766,
      "metadata": {
        "filename": "characters.txt",
        "chunk_index": 5,
        "document_id": "doc_abc"
      }
    }
  ],
  "context_used": "Full context string if include_context=true",
  "metadata": {
    "chunks_used": 5,
    "total_chunks_available": 150,
    "context_length": 2500,
    "answer_length": 350,
    "processing_time_seconds": 2.5,
    "model": "gemini-2.0-flash-exp",
    "embedding_model": "text-embedding-004"
  }
}
```

#### Error Responses

**404 - No Documents**
```json
{
  "detail": "No documents found. Please upload and embed documents first."
}
```

**404 - No Matches**
```json
{
  "detail": "No relevant information found for your question."
}
```

**500 - AI Service Error**
```json
{
  "detail": "AI service error: [error message]"
}
```

---

### 2. GET /api/rag/stats

Kiểm tra trạng thái RAG system.

#### Request

```bash
GET /api/rag/stats
```

#### Response

```json
{
  "ready": true,
  "total_documents": 3,
  "total_chunks": 150,
  "status": "ready",
  "message": "RAG system ready with 3 documents and 150 chunks",
  "collection_name": "documents",
  "embedding_model": "text-embedding-004",
  "chat_model": "gemini-2.0-flash-exp"
}
```

**Status Values:**
- `"ready"`: System có data, ready for queries ✅
- `"no_data"`: Chưa có documents, cần upload ⚠️
- `"error"`: Database error ❌

---

## 💡 Usage Examples

### Example 1: Basic Query

```bash
curl -X POST http://localhost:3201/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Giyu Tomioka là ai?",
    "n_results": 5
  }'
```

### Example 2: Query với Context

```bash
curl -X POST http://localhost:3201/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Shinobu Kocho có tính cách như thế nào?",
    "n_results": 3,
    "include_context": true
  }'
```

### Example 3: Filter by Document

```bash
curl -X POST http://localhost:3201/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who are the main characters?",
    "n_results": 10,
    "document_id": "doc_abc123"
  }'
```

### Example 4: Python Client

```python
import requests

response = requests.post(
    "http://localhost:3201/api/rag/query",
    json={
        "question": "Giyu Tomioka là ai?",
        "n_results": 5,
        "include_context": False
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])} chunks")
```

### Example 5: Check Stats

```bash
curl http://localhost:3201/api/rag/stats
```

---

## 🧪 Testing Guide

### Prerequisites

1. **Server running**
   ```bash
   cd 60days-rag
   python main.py
   ```

2. **Documents uploaded & embedded**
   ```bash
   python test_document_api.py
   ```

### Run RAG Tests

```bash
python test_rag_query.py
```

**Test Script Features:**
- ✅ Check RAG stats
- ✅ Test multiple queries
- ✅ Show answers + sources
- ✅ Display metadata & timing
- ✅ Formatted output

### Manual Testing

**Step 1: Check stats**
```bash
curl http://localhost:3201/api/rag/stats
```

**Step 2: Test query**
```bash
curl -X POST http://localhost:3201/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Giyu Tomioka là ai?","n_results":5}'
```

**Step 3: Check server logs**
- Server console shows detailed workflow:
  - ✅ Step 1: Checking DB
  - 🎯 Step 2: Embedding question
  - 🔍 Step 3: Searching chunks
  - 📝 Step 4: Building context
  - 💭 Step 5: Creating prompt
  - 🤖 Step 6: Calling Gemini
  - 📦 Step 7: Formatting response

---

## 🎓 Best Practices

### 1. Choosing N_Results

```python
# Small query (specific info)
n_results = 3  # Fast, focused

# Medium query (balanced)
n_results = 5-10  # Recommended ✅

# Complex query (comprehensive)
n_results = 15-20  # Expensive, but thorough
```

### 2. Prompt Engineering Principles

Our RAG implementation uses:

```
Instructions (how to answer)
    ↓
Context (relevant chunks)
    ↓
Question (user's query)
    ↓
Output Format (structure)
```

**Key principles:**
- ✅ "Answer ONLY based on context" → No hallucination
- ✅ "Cite sources [Source 1]" → Traceability
- ✅ "Same language as question" → Vietnamese/English flexibility
- ✅ "Say 'no info' if context insufficient" → Honesty

### 3. Error Handling

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise for 4xx/5xx
    result = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("No documents or no matches")
    elif e.response.status_code == 500:
        print("Server error")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Performance Optimization

| Metric | Impact | Optimization |
|--------|--------|--------------|
| **Embedding** | ~200ms | Batch questions if many |
| **Vector Search** | ~50ms | Use filters (document_id) |
| **Gemini API** | ~2s | Reduce n_results if slow |
| **Total** | ~2.5s | Acceptable for most use cases |

### 5. Context Window Management

**Gemini Limit:** 30,720 tokens (~100k characters)

```python
# Safe approach
n_results = 5  # ~2,500 chars context
# Rarely hits limit

# Aggressive approach  
n_results = 20  # ~10,000 chars context
# Risk hitting limit if chunks are large
```

---

## 🔧 Troubleshooting

### Issue 1: "No documents found"

**Problem:** RAG query returns 404

**Solutions:**
1. Check stats: `curl http://localhost:3201/api/rag/stats`
2. Upload documents: `python test_document_api.py`
3. Verify ChromaDB: Check `chroma_db/` folder exists
4. Check server logs for errors

### Issue 2: "No relevant information found"

**Problem:** Query returns no matches

**Causes:**
- Question không liên quan đến documents
- Embeddings chưa capture semantic meaning
- Documents quá ít

**Solutions:**
1. Rephrase question (different words, same meaning)
2. Increase n_results (try 10-15)
3. Check if documents contain relevant info
4. Use `include_context=true` to debug

### Issue 3: Poor answer quality

**Problem:** AI answer không đúng hoặc vague

**Causes:**
- n_results quá thấp → missed important info
- n_results quá cao → confused by too much context
- Chunks không chứa đủ context

**Solutions:**
1. Tune n_results (start with 5, adjust)
2. Improve document chunking strategy
3. Check similarity scores (should be >0.7)
4. Review context used (`include_context=true`)

### Issue 4: Slow response

**Problem:** Query takes >5 seconds

**Causes:**
- Large n_results
- Many chunks in DB
- Gemini API latency
- Network issues

**Solutions:**
1. Reduce n_results (5 instead of 20)
2. Use document_id filter
3. Check Gemini API status
4. Monitor server logs for bottlenecks

### Issue 5: Server errors (500)

**Problem:** Internal server error

**Causes:**
- Gemini API key invalid/expired
- ChromaDB database corrupted
- Out of memory
- Code bugs

**Solutions:**
1. Check `.env` file (GOOGLE_API_KEY)
2. Test Gemini: `python test_client.py`
3. Restart server
4. Check server console for stack trace
5. Delete `chroma_db/` and re-upload documents

---

## 📝 Code Structure

### File: `app/api/rag.py`

```python
# Main components:
1. Pydantic Models (RAGQueryRequest, RAGQueryResponse)
2. RAG Query Endpoint (7-step workflow)
3. Stats Endpoint (system health check)

# Services used:
- EmbeddingService: text → vector
- VectorDBService: store & search vectors
- GeminiService: generate answers
```

### Detailed Workflow

```python
@router.post("/query")
async def rag_query(request: RAGQueryRequest):
    # Step 1: Validate (DB has documents?)
    stats = vector_db.get_collection_stats()
    
    # Step 2: Embed question
    question_embedding = embedding_service.embed_text(request.question)
    
    # Step 3: Search similar chunks
    search_results = vector_db.search(
        query_embedding=question_embedding,
        n_results=request.n_results
    )
    
    # Step 4: Build context
    context = "\n\n---\n\n".join([
        f"[Source {i}] {chunk['text']}"
        for i, chunk in enumerate(search_results['results'], 1)
    ])
    
    # Step 5: Create prompt
    prompt = f"""Answer based ONLY on context:
    
CONTEXT:
{context}

QUESTION: {request.question}
"""
    
    # Step 6: Generate answer
    answer = gemini_service.chat(prompt)
    
    # Step 7: Format response
    return RAGQueryResponse(
        success=True,
        answer=answer,
        sources=[...],
        metadata={...}
    )
```

---

## 🚀 Next Steps

### Phase 1: Basic RAG ✅ (Current)
- ✅ RAG query endpoint
- ✅ Stats endpoint
- ✅ Source citations
- ✅ Metadata tracking

### Phase 2: Advanced RAG (Next)
- ⏳ Multi-query expansion
- ⏳ Re-ranking results
- ⏳ Streaming responses
- ⏳ Query history

### Phase 3: Agentic RAG (Future)
- ⏳ LangGraph agents
- ⏳ Multi-step reasoning
- ⏳ Tool calling
- ⏳ Self-correction

---

## 📚 Resources

- [RAG Overview](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)

---

## 🙏 Credits

Project: 60 Days RAG Learning
Author: Learning FastAPI + RAG + LangChain
Framework: FastAPI + ChromaDB + Google Gemini

---

**Happy RAG Querying! 🚀**
