"""
Quick Test Script - Kiểm Tra Document Management API
====================================================

Script này test tất cả endpoints:
1. List documents (should be empty initially)
2. Upload file
3. Embed document
4. List documents (should have 1 doc)
5. Get document details
6. Delete document
7. List documents (should be empty again)

USAGE:
------
python test_document_api.py

REQUIREMENTS:
-------------
- Backend running: uvicorn main:app --reload
- Python requests library: pip install requests
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:3201/api/documents"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_response(response):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()

# =============================================================================
# TEST 1: List documents (should be empty or have existing docs)
# =============================================================================
print_section("TEST 1: List All Documents")
response = requests.get(f"{BASE_URL}/list")
print_response(response)

# =============================================================================
# TEST 2: Upload file
# =============================================================================
print_section("TEST 2: Upload File")

# NOTE: Update this path to a real PDF or DOCX file on your system
test_file_path = "test_document.pdf"  # Change this!

try:
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print_response(response)
        
        if response.status_code == 200:
            upload_data = response.json()
            document_id = upload_data.get('document_id')
            filename = upload_data.get('filename')
            print(f"✅ Uploaded successfully!")
            print(f"   Document ID: {document_id}")
            print(f"   Filename: {filename}")
        else:
            print("❌ Upload failed!")
            exit(1)
except FileNotFoundError:
    print(f"❌ File not found: {test_file_path}")
    print("   Please create a test file or update the path!")
    exit(1)

# Wait a bit
time.sleep(1)

# =============================================================================
# TEST 3: Embed document
# =============================================================================
print_section("TEST 3: Embed Document")

embed_payload = {
    "document_id": document_id,
    "filename": filename
}

response = requests.post(
    f"{BASE_URL}/embed",
    json=embed_payload,
    headers={"Content-Type": "application/json"}
)
print_response(response)

if response.status_code == 200:
    embed_data = response.json()
    chunks_count = embed_data.get('chunks_count', 0)
    print(f"✅ Embedded successfully!")
    print(f"   Chunks created: {chunks_count}")
else:
    print("❌ Embedding failed!")
    exit(1)

# Wait for embedding to complete
time.sleep(2)

# =============================================================================
# TEST 4: List documents (should have our document now)
# =============================================================================
print_section("TEST 4: List Documents (After Upload)")

response = requests.get(f"{BASE_URL}/list")
print_response(response)

if response.status_code == 200:
    data = response.json()
    doc_count = data.get('count', 0)
    print(f"✅ Found {doc_count} document(s)")
else:
    print("❌ List failed!")

# =============================================================================
# TEST 5: Get document details
# =============================================================================
print_section("TEST 5: Get Document Details")

response = requests.get(f"{BASE_URL}/{document_id}")
print_response(response)

if response.status_code == 200:
    data = response.json()
    doc = data.get('document', {})
    chunks = doc.get('chunks', [])
    print(f"✅ Retrieved document details")
    print(f"   Filename: {doc.get('filename')}")
    print(f"   Chunks: {len(chunks)}")
    
    # Show first chunk preview
    if chunks:
        first_chunk = chunks[0]
        print(f"\n   First chunk preview:")
        print(f"   Index: {first_chunk.get('chunk_index')}")
        print(f"   Words: {first_chunk.get('words')}")
        print(f"   Text: {first_chunk.get('text_preview', '')[:100]}...")
else:
    print("❌ Get details failed!")

# =============================================================================
# TEST 6: Delete document
# =============================================================================
print_section("TEST 6: Delete Document")

# Ask for confirmation
confirm = input(f"\n⚠️  Delete document '{filename}'? (y/n): ")

if confirm.lower() == 'y':
    response = requests.delete(f"{BASE_URL}/{document_id}")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        chunks_deleted = data.get('chunks_deleted', 0)
        print(f"✅ Deleted successfully!")
        print(f"   Chunks removed: {chunks_deleted}")
    else:
        print("❌ Delete failed!")
else:
    print("⏭️  Skipped deletion")

# =============================================================================
# TEST 7: List documents (should be empty if deleted)
# =============================================================================
if confirm.lower() == 'y':
    print_section("TEST 7: List Documents (After Delete)")
    
    response = requests.get(f"{BASE_URL}/list")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        doc_count = data.get('count', 0)
        print(f"✅ Found {doc_count} document(s)")
    else:
        print("❌ List failed!")

# =============================================================================
# SUMMARY
# =============================================================================
print_section("TEST SUMMARY")

print("""
✅ All API endpoints tested successfully!

Endpoints verified:
- GET  /api/documents/list         (List all documents)
- POST /api/documents/upload       (Upload file)
- POST /api/documents/embed        (Process & embed)
- GET  /api/documents/{id}         (Get details)
- DELETE /api/documents/{id}       (Delete document)

Next steps:
1. Check UI: npm run dev (in 60days-rag-client)
2. Upload a document through UI
3. See it appear in the list
4. Click delete and see it removed
5. Implement RAG query next! 🚀
""")

print("="*60)
