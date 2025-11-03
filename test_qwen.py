"""
Test script cho Qwen3 integration.

Script này test tất cả Qwen endpoints để verify integration hoạt động đúng.
Chạy script này sau khi:
1. Khởi động vLLM server (port 8000) với Qwen3-0.6B
2. Khởi động FastAPI server (python main.py)

Usage:
    python test_qwen.py
"""

import requests
import json
import time


# Configuration
API_BASE_URL = "http://localhost:8000"  # FastAPI server (không phải vLLM port!)
QWEN_ENDPOINTS = {
    "health": f"{API_BASE_URL}/qwen/health",
    "info": f"{API_BASE_URL}/qwen/info",
    "chat": f"{API_BASE_URL}/qwen/chat",
    "stream": f"{API_BASE_URL}/qwen/chat/stream"
}


def print_section(title: str):
    """In section header đẹp."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health_check():
    """
    Test 1: Health check endpoint.
    
    Kiểm tra xem:
    - FastAPI server có chạy không?
    - Qwen vLLM server có accessible không?
    """
    print_section("TEST 1: Health Check")
    
    try:
        print(f"→ Calling: GET {QWEN_ENDPOINTS['health']}")
        response = requests.get(QWEN_ENDPOINTS['health'], timeout=10)
        
        print(f"✓ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            print(f"✓ Service: {data.get('service')}")
            print(f"✓ Model: {data.get('model')}")
            print(f"✓ Server URL: {data.get('server_url')}")
            print("\n✅ PASSED: Qwen service is healthy!")
            return True
        else:
            print(f"✗ Error: {response.json()}")
            print("\n❌ FAILED: Qwen service is not healthy")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ FAILED: Cannot connect to FastAPI server")
        print("   → Make sure FastAPI is running: python main.py")
        return False
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_model_info():
    """
    Test 2: Model info endpoint.
    
    Lấy thông tin về Qwen model.
    """
    print_section("TEST 2: Model Information")
    
    try:
        print(f"→ Calling: GET {QWEN_ENDPOINTS['info']}")
        response = requests.get(QWEN_ENDPOINTS['info'], timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Model Name: {data.get('model_name')}")
            print(f"✓ Model Size: {data.get('model_size')}")
            print(f"✓ Context Length: {data.get('context_length')}")
            print(f"✓ API Format: {data.get('api_format')}")
            
            print("\n  Features:")
            for feature in data.get('features', []):
                print(f"    • {feature}")
            
            print("\n  Use Cases:")
            for use_case in data.get('use_cases', []):
                print(f"    • {use_case}")
            
            print("\n✅ PASSED: Info retrieved successfully")
            return True
        else:
            print(f"✗ Error: {response.json()}")
            print("\n❌ FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_non_streaming_chat():
    """
    Test 3: Non-streaming chat endpoint.
    
    Test simple Q&A với Qwen3.
    """
    print_section("TEST 3: Non-Streaming Chat")
    
    # Test message
    test_message = "What is FastAPI? Answer in 2 sentences."
    
    payload = {
        "message": test_message,
        "temperature": 0.7,
        "max_tokens": 200,
        "system_prompt": "You are a helpful assistant who gives concise answers."
    }
    
    try:
        print(f"→ Calling: POST {QWEN_ENDPOINTS['chat']}")
        print(f"→ Message: {test_message}")
        print(f"→ Temperature: {payload['temperature']}")
        print(f"→ Max Tokens: {payload['max_tokens']}")
        
        # Gửi request
        start_time = time.time()
        response = requests.post(
            QWEN_ENDPOINTS['chat'],
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start_time
        
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Response Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n  Conversation ID: {data.get('conversation_id')}")
            print(f"  Model: {data.get('model')}")
            
            # Token usage
            usage = data.get('usage', {})
            print(f"\n  Token Usage:")
            print(f"    • Prompt: {usage.get('prompt_tokens', 0)}")
            print(f"    • Completion: {usage.get('completion_tokens', 0)}")
            print(f"    • Total: {usage.get('total_tokens', 0)}")
            
            # Response text
            response_text = data.get('response', '')
            print(f"\n  Response:")
            print(f"  {'-' * 66}")
            print(f"  {response_text}")
            print(f"  {'-' * 66}")
            
            print("\n✅ PASSED: Chat response received successfully")
            return True
        else:
            print(f"✗ Error: {response.json()}")
            print("\n❌ FAILED")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ FAILED: Request timeout (check vLLM server)")
        return False
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_streaming_chat():
    """
    Test 4: Streaming chat endpoint.
    
    Test real-time streaming response.
    """
    print_section("TEST 4: Streaming Chat (Real-time)")
    
    test_message = "Count from 1 to 10 and explain each number briefly."
    
    payload = {
        "message": test_message,
        "temperature": 0.7,
        "max_tokens": 500,
        "system_prompt": "You are a helpful assistant."
    }
    
    try:
        print(f"→ Calling: POST {QWEN_ENDPOINTS['stream']}")
        print(f"→ Message: {test_message}")
        print(f"\n  Streaming Response:")
        print(f"  {'-' * 66}")
        
        # Gửi streaming request
        response = requests.post(
            QWEN_ENDPOINTS['stream'],
            json=payload,
            stream=True,  # Enable streaming
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"✗ Error: Status {response.status_code}")
            print("\n❌ FAILED")
            return False
        
        # Đọc và in từng chunk
        chunk_count = 0
        conversation_id = None
        
        for line in response.iter_lines():
            if not line:
                continue
            
            # Decode line
            line = line.decode('utf-8')
            
            # Parse SSE format: "data: {...}"
            if line.startswith('data: '):
                data_str = line[6:]  # Remove "data: " prefix
                
                try:
                    chunk_data = json.loads(data_str)
                    
                    # Extract info
                    chunk_text = chunk_data.get('chunk', '')
                    is_done = chunk_data.get('done', False)
                    conversation_id = chunk_data.get('conversation_id')
                    
                    # In chunk (không xuống dòng)
                    if chunk_text:
                        print(chunk_text, end='', flush=True)
                        chunk_count += 1
                    
                    # Nếu done, break
                    if is_done:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        print(f"\n  {'-' * 66}")
        print(f"\n  Chunks Received: {chunk_count}")
        print(f"  Conversation ID: {conversation_id}")
        
        print("\n✅ PASSED: Streaming chat works correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_with_system_prompt():
    """
    Test 5: Chat với custom system prompt.
    
    Test khả năng customize behavior của model.
    """
    print_section("TEST 5: Custom System Prompt")
    
    test_cases = [
        {
            "name": "Python Expert",
            "system_prompt": "You are an expert Python programmer who writes clean, efficient code.",
            "message": "Write a function to reverse a string."
        },
        {
            "name": "Poet",
            "system_prompt": "You are a poet who speaks in rhymes.",
            "message": "Describe a beautiful sunset."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test Case {i}: {test_case['name']}")
        print(f"  {'-' * 66}")
        print(f"  System Prompt: {test_case['system_prompt']}")
        print(f"  Message: {test_case['message']}")
        
        payload = {
            "message": test_case['message'],
            "temperature": 0.8,
            "max_tokens": 200,
            "system_prompt": test_case['system_prompt']
        }
        
        try:
            response = requests.post(
                QWEN_ENDPOINTS['chat'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n  Response:")
                print(f"  {data.get('response')}")
                print(f"  ✓ Passed")
            else:
                print(f"  ✗ Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            return False
    
    print("\n✅ PASSED: System prompts work correctly")
    return True


def run_all_tests():
    """Chạy tất cả tests."""
    print("\n" + "=" * 70)
    print("  QWEN3 INTEGRATION TEST SUITE")
    print("=" * 70)
    print("\n  Testing Qwen3-0.6B integration with FastAPI")
    print(f"  API URL: {API_BASE_URL}")
    print("\n  Prerequisites:")
    print("  1. ✓ vLLM server running on port 8000")
    print("  2. ✓ FastAPI server running (python main.py)")
    print("  3. ✓ Qwen3-0.6B model loaded in vLLM")
    
    input("\n  Press Enter to start tests...")
    
    # Run tests
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    if not results[0][1]:
        print("\n" + "=" * 70)
        print("  ⚠️  Cannot proceed: Health check failed")
        print("  Please ensure:")
        print("  1. vLLM is running: vllm serve Qwen/Qwen3-0.6B --port 8000")
        print("  2. FastAPI is running: python main.py")
        print("=" * 70)
        return
    
    # Continue with other tests
    results.append(("Model Info", test_model_info()))
    results.append(("Non-Streaming Chat", test_non_streaming_chat()))
    results.append(("Streaming Chat", test_streaming_chat()))
    results.append(("System Prompts", test_with_system_prompt()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<30} {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Qwen integration is working perfectly!")
    else:
        print("\n  ⚠️  Some tests failed. Please check the errors above.")
    
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n  Tests interrupted by user.")
    except Exception as e:
        print(f"\n\n  Unexpected error: {str(e)}")
