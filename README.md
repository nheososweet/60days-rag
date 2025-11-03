# 60 Days RAG - FastAPI + LLM + RAG Learning Project

A comprehensive FastAPI project for learning and implementing:

- **FastAPI**: Modern, fast Python web framework
- **LLM Integration**: Google Gemini AI with streaming support
- **RAG**: Retrieval-Augmented Generation
- **LangChain**: LLM application framework
- **LangGraph**: Agent orchestration and workflows
- **Vector Databases**: Semantic search and embeddings

## 🌟 Features

### ✅ Currently Implemented

- FastAPI application with proper project structure
- Google Gemini AI integration
- Streaming chat endpoints (Server-Sent Events)
- Non-streaming chat endpoints
- Health check and monitoring
- CORS middleware configuration
- Environment-based configuration
- Comprehensive API documentation (Swagger/ReDoc)

### 🚧 Coming Soon

- Document ingestion and processing
- Vector database integration (ChromaDB, Pinecone)
- RAG query with context retrieval
- LangChain integration for advanced workflows
- Agentic RAG implementation
- LangGraph multi-agent systems
- PDF/DOCX document parsing
- Conversation history management

## 📁 Project Structure

```
60days-rag/
├── app/
│   ├── __init__.py
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat endpoints with streaming
│   │   ├── rag.py             # RAG endpoints (skeleton)
│   │   └── health.py          # Health check endpoints
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   └── config.py          # Settings management
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py         # Request/response models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── gemini_service.py  # Gemini AI integration
│   │   └── rag_service.py     # RAG service (skeleton)
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── logger.py          # Logging utilities
├── data/                       # Data storage
│   └── chroma/                # Vector database (ChromaDB)
├── docs/                       # Additional documentation
├── tests/                      # Test suite
│   └── test_api.py
├── .env.example               # Environment variables template
├── .gitignore
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Google Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory:**

   ```powershell
   cd c:\Data\AI\60days-rag
   ```

2. **Activate your virtual environment:**

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```powershell
   pip install fastapi uvicorn pydantic-settings python-multipart
   ```

4. **Create `.env` file from template:**

   ```powershell
   Copy-Item .env.example .env
   ```

5. **Edit `.env` and add your Gemini API key:**
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### Running the Application

1. **Start the FastAPI server:**

   ```powershell
   python main.py
   ```

   Or with uvicorn directly:

   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API:**
   - **Interactive API Docs (Swagger):** http://localhost:8000/docs
   - **Alternative Docs (ReDoc):** http://localhost:8000/redoc
   - **Health Check:** http://localhost:8000/health
   - **Root Endpoint:** http://localhost:8000/

## 📚 API Endpoints

### Health & Status

- **GET /** - Root endpoint with API information
- **GET /health** - Health check and service status

### Chat Endpoints

- **POST /chat/** - Send message to Gemini AI (non-streaming)

  ```json
  {
    "message": "What is RAG?",
    "temperature": 0.7,
    "stream": false
  }
  ```

- **POST /chat/stream** - Send message with streaming response (SSE)

  ```json
  {
    "message": "Explain LangChain in detail",
    "temperature": 0.7
  }
  ```

- **GET /chat/health** - Check chat service health

### RAG Endpoints (Coming Soon)

- **POST /rag/query** - Query knowledge base (non-streaming)
- **POST /rag/query/stream** - Query with streaming response
- **POST /rag/documents/upload** - Upload document to knowledge base
- **GET /rag/collections** - List all collections
- **DELETE /rag/collections/{name}** - Delete a collection

## 💡 Usage Examples

### Non-Streaming Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/chat/",
    json={
        "message": "What is Retrieval-Augmented Generation?",
        "temperature": 0.7
    }
)

print(response.json()["response"])
```

### Streaming Chat (JavaScript/Fetch)

```javascript
const eventSource = new EventSource("http://localhost:8000/chat/stream", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    message: "Explain RAG in detail",
  }),
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.done) {
    eventSource.close();
  } else {
    console.log(data.chunk);
  }
};
```

### Streaming Chat (Python with SSE client)

```python
import requests
import json

def stream_chat(message: str):
    response = requests.post(
        "http://localhost:8000/chat/stream",
        json={"message": message},
        stream=True
    )

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if not data['done']:
                    print(data['chunk'], end='', flush=True)
                else:
                    print()
                    break

stream_chat("What is LangChain?")
```

## 🔧 Configuration

Configuration is managed via environment variables in `.env` file:

```env
# Google Gemini API
GEMINI_API_KEY=your_api_key

# Application
APP_NAME=60days-rag
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Model Settings
DEFAULT_MODEL=gemini-2.5-flash
TEMPERATURE=0.7
MAX_TOKENS=2048
```

## 📦 Future Enhancements

### Phase 1: Core RAG (Weeks 1-2)

- [ ] Implement vector database (ChromaDB)
- [ ] Document chunking and embedding
- [ ] Semantic search and retrieval
- [ ] Context-aware response generation

### Phase 2: LangChain Integration (Weeks 3-4)

- [ ] LangChain document loaders
- [ ] Chain composition for complex workflows
- [ ] Memory management for conversations
- [ ] Multiple LLM provider support

### Phase 3: Agentic RAG (Weeks 5-6)

- [ ] Agent-based architecture
- [ ] Tool calling and function execution
- [ ] Multi-step reasoning
- [ ] Self-correction mechanisms

### Phase 4: LangGraph (Weeks 7-8)

- [ ] State graph implementation
- [ ] Multi-agent orchestration
- [ ] Complex workflow management
- [ ] Agent collaboration patterns

## 🧪 Testing

Run tests with pytest:

```powershell
pip install pytest pytest-asyncio httpx
pytest tests/
```

## 📖 Learning Resources

- **FastAPI:** https://fastapi.tiangolo.com/
- **LangChain:** https://python.langchain.com/
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **Google Gemini:** https://ai.google.dev/
- **ChromaDB:** https://docs.trychroma.com/

## 🤝 Contributing

This is a learning project. Feel free to:

- Add new features
- Improve documentation
- Report issues
- Share your learning experience

## 📝 License

This project is for educational purposes.

## 🙋‍♂️ Support

For questions or issues:

1. Check the `/docs` endpoint for API documentation
2. Review the code comments
3. Experiment with the interactive API docs

Happy learning! 🚀
