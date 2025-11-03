"""
Quick test để verify thinking mode có hoạt động không.
"""

import requests
import json

# Test với curl command mà bạn đã dùng
url = "http://127.0.0.1:3201/qwen/chat/stream"

payload = {
    "message": "Explain what is RAG in AI? Think carefully about it first.",
    "stream": True,
    "temperature": 0.7,
    "enable_thinking": True,
    "system_prompt": "You are an AI expert. Show your thinking process before answering."
}

print("🚀 Testing Qwen3 Thinking Mode")
print("=" * 60)
print(f"Request: {json.dumps(payload, indent=2)}")
print("=" * 60)
print("\nResponse:\n")

response = requests.post(url, json=payload, stream=True)

thinking_found = False
content_chunks = []

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            
            chunk_type = data.get("type", "unknown")
            
            if chunk_type == "thinking":
                thinking_found = True
                print(f"💭 [THINKING]: {data.get('thinking_content', '')}\n")
                print("-" * 60)
            
            elif chunk_type == "content":
                chunk = data.get("chunk", "")
                if chunk:
                    content_chunks.append(chunk)
                    print(chunk, end="", flush=True)
            
            elif data.get("done"):
                break

print("\n" + "=" * 60)
print(f"\n✅ Thinking mode detected: {thinking_found}")
if not thinking_found:
    print("⚠️  Model didn't generate <think> tags. Try:")
    print("   1. More explicit prompt: 'Think step by step before answering'")
    print("   2. Using larger model: Qwen2.5-7B or QwQ-32B-Preview")
