"""
Test Qwen3 vLLM với thinking mode.
Run này sau khi vLLM server đã start.
"""
import requests
import json

print("🧪 Testing Qwen3 vLLM Server")
print("=" * 80)

# Test 1: Basic health check
print("\n1️⃣ Health Check")
print("-" * 80)
try:
    response = requests.get("http://localhost:8000/v1/models", timeout=5)
    if response.status_code == 200:
        models = response.json()
        print("✅ vLLM server is running")
        print(f"📦 Available models: {json.dumps(models, indent=2)}")
    else:
        print(f"⚠️  Server responded with status {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to vLLM server: {e}")
    print("Make sure vLLM is running on port 8000")
    exit(1)

# Test 2: Simple completion WITHOUT enable_thinking
print("\n\n2️⃣ Test WITHOUT enable_thinking (baseline)")
print("-" * 80)
try:
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "Qwen/Qwen3-0.6B",
            "messages": [
                {"role": "user", "content": "What is 2+2? Answer briefly."}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"Response: {content}")
        
        if "<think>" in content:
            print("⚠️  Model generated <think> tags even without enable_thinking!")
        else:
            print("✅ Normal response (no thinking tags)")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: WITH enable_thinking in extra_body
print("\n\n3️⃣ Test WITH enable_thinking=true (main test)")
print("-" * 80)
try:
    payload = {
        "model": "Qwen/Qwen3-0.6B",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful assistant. Show your thinking process before answering."
            },
            {
                "role": "user", 
                "content": "What is 2+2? Think step by step carefully."
            }
        ],
        "max_tokens": 512,
        "temperature": 0.6,
        "top_p": 0.95,
        "top_k": 20,
        "extra_body": {
            "enable_thinking": True
        }
    }
    
    print(f"📤 Request payload:")
    print(json.dumps(payload, indent=2))
    print("\n📥 Response:")
    print("-" * 80)
    
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        print(f"Raw content:\n{content}\n")
        print("-" * 80)
        
        # Check for thinking tags
        if "<think>" in content and "</think>" in content:
            print("✅ SUCCESS! Model generated <think> tags!")
            
            # Parse thinking content
            think_start = content.find("<think>")
            think_end = content.find("</think>")
            
            thinking = content[think_start + 7:think_end].strip()
            answer = content[think_end + 8:].strip()
            
            print(f"\n💭 Thinking process:")
            print(f"   {thinking}")
            print(f"\n💬 Final answer:")
            print(f"   {answer}")
            
        elif "<think>" in content:
            print("⚠️  Found <think> tag but no closing </think> tag")
            print("Model may have generated incomplete thinking content")
            
        else:
            print("❌ No <think> tags found in response!")
            print("\nPossible reasons:")
            print("1. vLLM không support enable_thinking parameter")
            print("2. extra_body không được pass đúng cách")
            print("3. Model không generate <think> tags với prompt này")
            print("\n💡 Try stronger prompt hoặc system message")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Streaming test
print("\n\n4️⃣ Test STREAMING with enable_thinking")
print("-" * 80)
try:
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "Qwen/Qwen3-0.6B",
            "messages": [
                {"role": "user", "content": "Count from 1 to 5. Think about it first."}
            ],
            "max_tokens": 256,
            "temperature": 0.6,
            "stream": True,
            "extra_body": {
                "enable_thinking": True
            }
        },
        stream=True,
        timeout=30
    )
    
    if response.status_code == 200:
        print("Streaming response:")
        full_content = ""
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(data_str)
                        if chunk.get("choices") and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                                full_content += content
                    except json.JSONDecodeError:
                        continue
        
        print("\n" + "-" * 80)
        if "<think>" in full_content:
            print("✅ Streaming với thinking tags works!")
        else:
            print("⚠️  No thinking tags in streaming response")
    else:
        print(f"❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Summary
print("\n\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print("""
Next steps:
1. If <think> tags detected → Your FastAPI service should work!
   Run: python quick_test_thinking.py

2. If NO <think> tags:
   - vLLM may not support enable_thinking with current flags
   - Try stronger prompts: "Think carefully step by step"
   - Check vLLM startup logs for reasoning parser info
   
3. Test FastAPI endpoint:
   curl -X POST http://127.0.0.1:3201/qwen/chat/stream \\
     -H "Content-Type: application/json" \\
     -d '{"message": "What is RAG?", "enable_thinking": true}'
""")
