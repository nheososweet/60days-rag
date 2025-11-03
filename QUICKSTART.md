# 🚀 Quick Start Guide

## Prerequisites Check

✅ Python 3.9+ installed  
✅ Virtual environment created (`venv`)  
✅ Project structure created  
✅ Gemini API key available

## Step-by-Step Setup (5 minutes)

### 1. Activate Virtual Environment

```powershell
cd c:\Data\AI\60days-rag
.\venv\Scripts\Activate.ps1
```

### 2. Install Required Packages

```powershell
pip install fastapi uvicorn[standard] pydantic-settings python-multipart
```

Expected output:

```
Successfully installed fastapi-... uvicorn-... pydantic-settings-... python-multipart-...
```

### 3. Verify Installation

```powershell
python -c "import fastapi; import uvicorn; print('✅ Ready to go!')"
```

### 4. Verify .env File

Your `.env` file should already have your Gemini API key:

```env
GEMINI_API_KEY=AIzaSyATN96rHdWVkZdhTpyZ3FNtoYt1AdjHWt0
```

### 5. Start the Server

```powershell
python main.py
```

Expected output:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test the API

Open your browser:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

### 7. Try Your First Chat (Optional)

In a new PowerShell window:

```powershell
cd c:\Data\AI\60days-rag
.\venv\Scripts\Activate.ps1
python test_client.py
```

## What You Can Do Now

### 1. Interactive API Documentation

Visit http://localhost:8000/docs and try:

- **POST /chat/** - Send a message
- **POST /chat/stream** - Get streaming response
- **GET /health** - Check API health

### 2. Non-Streaming Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/chat/",
    json={"message": "Hello, explain RAG briefly"}
)
print(response.json()["response"])
```

### 3. Streaming Chat

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/chat/stream",
    json={"message": "Explain FastAPI"},
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if not data['done']:
                print(data['chunk'], end='', flush=True)
```

## Troubleshooting

### ❌ Import Error: No module named 'fastapi'

**Solution:**

```powershell
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn[standard] pydantic-settings python-multipart
```

### ❌ Error: GEMINI_API_KEY not found

**Solution:** Check your `.env` file exists and has the correct API key

### ❌ Port 8000 already in use

**Solution:**

```powershell
# Change port in .env file
PORT=8001

# Or run with custom port
uvicorn main:app --port 8001
```

### ❌ Connection refused when running test_client.py

**Solution:** Make sure the server is running first (`python main.py`)

## Next Steps

Now that your API is running:

1. ✅ Explore the interactive docs at `/docs`
2. ✅ Try different chat parameters (temperature, model)
3. ✅ Test streaming vs non-streaming
4. 📚 Read `docs/LEARNING_PLAN.md` for your 60-day journey
5. 📚 Review `docs/ARCHITECTURE.md` to understand the structure
6. 🔨 Start adding RAG features (Week 3-4)

## Key Files Reference

- `main.py` - Application entry point
- `app/api/chat.py` - Chat endpoints
- `app/services/gemini_service.py` - Gemini integration
- `.env` - Configuration
- `README.md` - Full documentation

## Getting Help

1. Check the interactive docs: http://localhost:8000/docs
2. Review error messages in terminal
3. Read the code comments
4. Check `docs/` folder for guides

Happy coding! 🎉
