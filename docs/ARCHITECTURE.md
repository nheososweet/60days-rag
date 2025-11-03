# API Architecture

## Overview

The 60days-rag API follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                        │
│            (Web, Mobile, CLI, etc.)                     │
└─────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  Health  │  │   Chat   │  │        RAG           │  │
│  │ Endpoints│  │ Endpoints│  │     Endpoints        │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│  ┌───────────────────┐  ┌──────────────────────────┐   │
│  │  Gemini Service   │  │     RAG Service          │   │
│  │  - Chat           │  │  - Document Ingestion    │   │
│  │  - Streaming      │  │  - Retrieval             │   │
│  │  - Generation     │  │  - Generation            │   │
│  └───────────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│              External Services Layer                    │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────┐    │
│  │  Gemini  │  │  ChromaDB  │  │    LangChain     │    │
│  │   API    │  │  (Vector)  │  │   (Future)       │    │
│  └──────────┘  └────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. API Layer (`app/api/`)

- **Purpose**: Handle HTTP requests/responses
- **Responsibilities**:
  - Request validation (Pydantic models)
  - Response formatting
  - Error handling
  - Streaming support (SSE)
  - Route definitions
- **Files**:
  - `chat.py` - Chat endpoints
  - `rag.py` - RAG endpoints
  - `health.py` - Health checks

### 2. Service Layer (`app/services/`)

- **Purpose**: Business logic and external API interactions
- **Responsibilities**:
  - LLM interaction (Gemini)
  - Document processing
  - Vector operations
  - Context management
  - Streaming logic
- **Files**:
  - `gemini_service.py` - Gemini AI integration
  - `rag_service.py` - RAG operations

### 3. Models Layer (`app/models/`)

- **Purpose**: Data validation and serialization
- **Responsibilities**:
  - Request/response schemas
  - Data validation
  - Type safety
  - API documentation
- **Files**:
  - `schemas.py` - Pydantic models

### 4. Core Layer (`app/core/`)

- **Purpose**: Application configuration
- **Responsibilities**:
  - Environment variable management
  - Application settings
  - Constants
- **Files**:
  - `config.py` - Settings and configuration

### 5. Utils Layer (`app/utils/`)

- **Purpose**: Shared utilities
- **Responsibilities**:
  - Logging
  - Helpers
  - Common functions
- **Files**:
  - `logger.py` - Logging utilities

## Data Flow

### Chat Request Flow

```
1. Client → POST /chat/stream
2. API validates request (ChatRequest model)
3. API calls gemini_service.generate_stream_response()
4. Service configures Gemini API
5. Service streams chunks from Gemini
6. API formats chunks as SSE
7. Client receives streaming response
```

### RAG Query Flow (Future)

```
1. Client → POST /rag/query/stream
2. API validates request (RAGQueryRequest model)
3. API calls rag_service.query_rag_stream()
4. Service retrieves relevant documents from vector DB
5. Service builds context from documents
6. Service generates answer with Gemini + context
7. Service streams response
8. API formats as SSE with sources
9. Client receives answer + sources
```

## Error Handling

Errors are handled at multiple levels:

1. **Validation Errors**: Pydantic models (400 Bad Request)
2. **Service Errors**: Try/catch in services (500 Internal Error)
3. **API Errors**: HTTPException (4xx/5xx)
4. **Global Handler**: Catches all unhandled exceptions

## Streaming Architecture

The API supports Server-Sent Events (SSE) for real-time streaming:

```
┌──────────┐                  ┌──────────┐                  ┌──────────┐
│  Client  │                  │   API    │                  │  Gemini  │
└────┬─────┘                  └────┬─────┘                  └────┬─────┘
     │                             │                             │
     │  POST /chat/stream          │                             │
     │─────────────────────────────>                             │
     │                             │                             │
     │                             │  generate_content_stream()  │
     │                             │─────────────────────────────>
     │                             │                             │
     │  data: {"chunk": "Hello"}   │         chunk: "Hello"      │
     │<─────────────────────────────────────────────────────────│
     │                             │                             │
     │  data: {"chunk": "World"}   │         chunk: "World"      │
     │<─────────────────────────────────────────────────────────│
     │                             │                             │
     │  data: {"done": true}       │         (complete)          │
     │<─────────────────────────────────────────────────────────│
     │                             │                             │
```

## Configuration Management

Configuration uses a hierarchy:

1. **Environment Variables** (.env file)
2. **Default Values** (in config.py)
3. **Runtime Override** (via request parameters)

Example:

```python
# Default from config
temperature = settings.TEMPERATURE  # 0.7

# Override from request
temperature = request.temperature or settings.TEMPERATURE
```

## Future Architecture Enhancements

### LangChain Integration

```
┌───────────────────────────────────────────┐
│         LangChain Components              │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Chains  │  │  Agents  │  │ Memory  │ │
│  └──────────┘  └──────────┘  └─────────┘ │
└───────────────────────────────────────────┘
```

### LangGraph Workflow

```
┌──────────────────────────────────────────┐
│          State Graph                     │
│                                          │
│  ┌─────┐    ┌─────┐    ┌─────┐         │
│  │Agent│───>│Agent│───>│Agent│         │
│  │  1  │    │  2  │    │  3  │         │
│  └─────┘    └─────┘    └─────┘         │
│     │          │          │             │
│     └──────────┴──────────┘             │
│           Shared State                  │
└──────────────────────────────────────────┘
```

## Performance Considerations

1. **Async/Await**: All I/O operations are async
2. **Streaming**: Reduces time-to-first-byte
3. **Caching**: Future implementation for embeddings
4. **Connection Pooling**: For database connections

## Security

1. **API Key Protection**: Environment variables
2. **CORS**: Configurable origins
3. **Input Validation**: Pydantic models
4. **Rate Limiting**: To be implemented
5. **Authentication**: To be implemented
