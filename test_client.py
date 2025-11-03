"""
Simple test client to demonstrate API usage.
Run this after starting the FastAPI server.
"""
import requests
import json


def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_chat():
    """Test non-streaming chat."""
    print("\n=== Testing Chat Endpoint (Non-Streaming) ===")
    response = requests.post(
        "http://localhost:8000/chat/",
        json={
            "message": "What is RAG in AI? Answer in 2 sentences.",
            "temperature": 0.7
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response']}")
        print(f"Model: {data['model']}")
        print(f"Conversation ID: {data['conversation_id']}")


def test_chat_stream():
    """Test streaming chat."""
    print("\n=== Testing Chat Endpoint (Streaming) ===")
    response = requests.post(
        "http://localhost:8000/chat/stream",
        json={
            "message": "Explain LangChain in 3 sentences.",
            "temperature": 0.7
        },
        stream=True
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Streaming response:")
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if not data['done']:
                        print(data['chunk'], end='', flush=True)
                    else:
                        print("\n")
                        print(f"Conversation ID: {data['conversation_id']}")
                        break


def test_rag_query():
    """Test RAG query (skeleton - will show placeholder)."""
    print("\n=== Testing RAG Query Endpoint (Skeleton) ===")
    response = requests.post(
        "http://localhost:8000/rag/query",
        json={
            "query": "What are the benefits of RAG?",
            "top_k": 5
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer']}")
        print(f"Sources: {data['sources']}")


if __name__ == "__main__":
    print("=" * 60)
    print("60days-rag API Test Client")
    print("=" * 60)
    print("\nMake sure the FastAPI server is running on http://localhost:8000")
    print("Start it with: python main.py")
    
    try:
        # Test all endpoints
        test_health()
        test_chat()
        test_chat_stream()
        test_rag_query()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API.")
        print("Please make sure the FastAPI server is running:")
        print("  python main.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
