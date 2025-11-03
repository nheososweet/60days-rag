"""
Test script để verify Qwen3 thinking mode.

Script này test 2 cases:
1. enable_thinking=False - Normal response
2. enable_thinking=True - Response với thinking process
"""

import requests
import json

BASE_URL = "http://127.0.0.1:3201"

def test_streaming_with_thinking():
    """Test streaming endpoint với thinking mode."""
    print("=" * 80)
    print("TEST 1: STREAMING với THINKING MODE ENABLED")
    print("=" * 80)
    
    payload = {
        "message": "What is 2+2? Think carefully step by step.",
        "temperature": 0.7,
        "enable_thinking": True,
        "system_prompt": "You are a math tutor. Always show your reasoning process."
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    print(f"\n📥 Response Stream:\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/qwen/chat/stream",
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return
        
        thinking_content = ""
        final_content = ""
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        chunk = json.loads(data_str)
                        
                        # Check chunk type
                        chunk_type = chunk.get("type", "content")
                        
                        if chunk_type == "thinking":
                            thinking_content = chunk.get("thinking_content", "")
                            print(f"💭 [THINKING]: {thinking_content}\n")
                        
                        elif chunk_type == "content":
                            content = chunk.get("chunk", "")
                            if content:
                                final_content += content
                                print(content, end="", flush=True)
                        
                        elif chunk_type == "finish":
                            print(f"\n✅ [FINISH]: {chunk.get('finish_reason', 'stop')}")
                        
                        elif chunk_type == "error":
                            print(f"\n❌ [ERROR]: {chunk.get('chunk', 'Unknown error')}")
                        
                        # Old format compatibility
                        elif "chunk" in chunk and chunk.get("done") == True:
                            print("\n✅ Stream completed")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  JSON decode error: {e}")
                        continue
        
        print("\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        if thinking_content:
            print(f"💭 Thinking: {thinking_content}")
        else:
            print("⚠️  No thinking content detected!")
        print(f"💬 Answer: {final_content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_streaming_without_thinking():
    """Test streaming endpoint WITHOUT thinking mode."""
    print("\n\n" + "=" * 80)
    print("TEST 2: STREAMING với THINKING MODE DISABLED (normal)")
    print("=" * 80)
    
    payload = {
        "message": "What is 2+2?",
        "temperature": 0.7,
        "enable_thinking": False
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    print(f"\n📥 Response Stream:\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/qwen/chat/stream",
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        chunk = json.loads(data_str)
                        
                        chunk_type = chunk.get("type", "content")
                        
                        if chunk_type == "content":
                            content = chunk.get("chunk", "")
                            if content:
                                print(content, end="", flush=True)
                        
                        elif chunk.get("done") == True:
                            print("\n✅ Stream completed")
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_non_streaming_with_thinking():
    """Test non-streaming endpoint với thinking mode."""
    print("\n\n" + "=" * 80)
    print("TEST 3: NON-STREAMING với THINKING MODE")
    print("=" * 80)
    
    payload = {
        "message": "Explain why the sky is blue in simple terms. Think about it first.",
        "temperature": 0.7,
        "enable_thinking": True,
        "system_prompt": "You are a science educator. Show your reasoning process."
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/qwen/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        print(f"\n📥 Response:")
        print("=" * 80)
        
        if "thinking_content" in result:
            print(f"💭 Thinking Process:")
            print(result.get("thinking_content", "N/A"))
            print("\n" + "-" * 80)
        
        print(f"💬 Final Answer:")
        print(result.get("response", "N/A"))
        
        print("\n" + "=" * 80)
        print(f"Model: {result.get('model', 'N/A')}")
        print(f"Conversation ID: {result.get('conversation_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n🚀 QWEN3 THINKING MODE TEST SUITE")
    print("=" * 80)
    print("Testing Qwen3-0.6B with thinking mode support")
    print("Make sure:")
    print("  1. vLLM server is running on http://localhost:8000")
    print("  2. FastAPI server is running on http://localhost:3201")
    print("=" * 80)
    
    # Run tests
    test_streaming_with_thinking()
    test_streaming_without_thinking()
    test_non_streaming_with_thinking()
    
    print("\n\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("\nNOTE: If you don't see thinking content, it might be because:")
    print("  1. Qwen3-0.6B model doesn't always use <think> tags")
    print("  2. Need more explicit prompting ('Think step by step')")
    print("  3. Consider using larger models like Qwen2.5-7B or QwQ-32B-Preview")
