# 📦 Package Installation Guide

## Current Packages (Already Installed)

Your `requirements.txt` already has:

- google-genai
- pydantic
- requests
- And their dependencies

## Required Additional Packages

To run the FastAPI application, you need to install these packages:

### Core FastAPI Packages

```powershell
pip install fastapi
pip install uvicorn[standard]
pip install pydantic-settings
pip install python-multipart
```

### Optional (for future features)

```powershell
# For RAG and vector databases
pip install langchain
pip install langchain-google-genai
pip install chromadb

# For document processing
pip install pypdf
pip install python-docx
pip install unstructured

# For testing
pip install pytest
pip install pytest-asyncio
pip install httpx

# For additional features
pip install python-dotenv
```

## Quick Install (All Core Packages)

Copy and paste this command to install all core dependencies:

```powershell
pip install fastapi uvicorn[standard] pydantic-settings python-multipart
```

## Verify Installation

After installation, verify with:

```powershell
python -c "import fastapi; import uvicorn; print('✅ FastAPI installed successfully!')"
```

## Update requirements.txt

After installing packages, update your requirements.txt:

```powershell
pip freeze > requirements_new.txt
```

Then review and merge the relevant packages into `requirements.txt`.

## Installing from requirements.txt (Future)

Once you have all packages in requirements.txt, others can install with:

```powershell
pip install -r requirements.txt
```

## Version Management

For production, pin specific versions:

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic-settings==2.1.0
python-multipart==0.0.6
```

For development, use latest versions (what we're doing now):

```txt
fastapi
uvicorn[standard]
pydantic-settings
python-multipart
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Make sure venv is activated and packages are installed

```powershell
.\venv\Scripts\Activate.ps1
pip install <package-name>
```

### Issue: Import errors

**Solution**: Restart your IDE/terminal after installing packages

### Issue: Version conflicts

**Solution**: Create a fresh virtual environment

```powershell
deactivate
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```
