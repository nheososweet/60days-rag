"""
Demo client để test và hiển thị streaming response với thinking content.
"""
import requests
import json
import sys
from typing import Optional

class QwenStreamClient:
    """Client để consume Qwen streaming API với thinking mode support."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:3201"):
        self.base_url = base_url
        
    def chat_stream(
        self,
        message: str,
        enable_thinking: bool = True,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        show_thinking: bool = True,
        show_chunks: bool = False
    ):
        """
        Stream chat với Qwen model.
        
        Args:
            message: User message
            enable_thinking: Enable thinking mode
            system_prompt: System instruction
            temperature: Generation temperature
            show_thinking: Hiển thị thinking process
            show_chunks: Hiển thị từng chunk (debug mode)
        """
        payload = {
            "message": message,
            "temperature": temperature,
            "enable_thinking": enable_thinking
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        print("=" * 80)
        print("🤖 QWEN3 CHAT (with Thinking Mode)")
        print("=" * 80)
        print(f"\n👤 You: {message}\n")
        
        if enable_thinking:
            print("💭 Thinking mode: ENABLED\n")
        
        try:
            response = requests.post(
                f"{self.base_url}/qwen/chat/stream",
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ Error: HTTP {response.status_code}")
                print(response.text)
                return
            
            # State tracking
            thinking_shown = False
            content_buffer = []
            conversation_id = None
            
            print("🤖 Qwen: ", end="", flush=True)
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    if line.startswith('data: '):
                        data_str = line[6:]
                        
                        try:
                            chunk = json.loads(data_str)
                            
                            # Debug: show raw chunks
                            if show_chunks:
                                print(f"\n[DEBUG] {chunk}", flush=True)
                            
                            chunk_type = chunk.get("type", "content")
                            conversation_id = chunk.get("conversation_id")
                            
                            # Handle thinking chunk
                            if chunk_type == "thinking" and show_thinking:
                                thinking_content = chunk.get("thinking_content", "")
                                if thinking_content and not thinking_shown:
                                    print(f"\n\n{'─' * 80}")
                                    print("💭 THINKING PROCESS:")
                                    print(f"{'─' * 80}")
                                    print(thinking_content)
                                    print(f"{'─' * 80}\n")
                                    print("🤖 Answer: ", end="", flush=True)
                                    thinking_shown = True
                            
                            # Handle content chunk
                            elif chunk_type == "content":
                                content = chunk.get("chunk", "")
                                if content:
                                    content_buffer.append(content)
                                    print(content, end="", flush=True)
                            
                            # Handle finish
                            elif chunk_type == "finish":
                                finish_reason = chunk.get("finish_reason", "stop")
                                print(f"\n\n{'─' * 80}")
                                print(f"✅ Complete (reason: {finish_reason})")
                                if conversation_id:
                                    print(f"📝 Conversation ID: {conversation_id}")
                                print("=" * 80)
                            
                            # Handle error
                            elif chunk_type == "error":
                                error_msg = chunk.get("chunk", "Unknown error")
                                print(f"\n❌ Error: {error_msg}")
                            
                            # Handle done signal (old format)
                            elif chunk.get("done") == True and chunk_type != "finish":
                                if not thinking_shown and not content_buffer:
                                    print("\n\n✅ Complete")
                                    print("=" * 80)
                                
                        except json.JSONDecodeError as e:
                            if show_chunks:
                                print(f"\n[JSON Error] {e}: {data_str}")
                            continue
            
            # Final newline
            if content_buffer:
                print()
                
        except requests.exceptions.Timeout:
            print("\n❌ Request timeout")
        except requests.exceptions.ConnectionError:
            print("\n❌ Cannot connect to server. Is it running?")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main demo function."""
    client = QwenStreamClient()
    
    # Example 1: Simple question with thinking
    print("\n" + "🔹" * 40)
    print("DEMO 1: Simple Math with Thinking")
    print("🔹" * 40 + "\n")
    
    client.chat_stream(
        message="What is 15 * 23? Calculate step by step.",
        enable_thinking=True,
        temperature=0.6
    )
    
    input("\n\n⏸️  Press Enter for next demo...")
    
    # Example 2: Vietnamese question
    print("\n" + "🔹" * 40)
    print("DEMO 2: Vietnamese Question with Thinking")
    print("🔹" * 40 + "\n")
    
    client.chat_stream(
        message="Hà Nội hôm nay thời tiết thế nào?",
        enable_thinking=True,
        system_prompt="Bạn là trợ lý AI thông minh, luôn suy nghĩ kỹ trước khi trả lời.",
        temperature=0.6
    )
    
    input("\n\n⏸️  Press Enter for next demo...")
    
    # Example 3: Without thinking (comparison)
    print("\n" + "🔹" * 40)
    print("DEMO 3: Same Question WITHOUT Thinking")
    print("🔹" * 40 + "\n")
    
    client.chat_stream(
        message="Hà Nội hôm nay thời tiết thế nào?",
        enable_thinking=False,
        temperature=0.7
    )
    
    input("\n\n⏸️  Press Enter for next demo...")
    
    # Example 4: Complex reasoning
    print("\n" + "🔹" * 40)
    print("DEMO 4: Complex Reasoning Task")
    print("🔹" * 40 + "\n")
    
    client.chat_stream(
        message="Explain what is RAG (Retrieval-Augmented Generation) in AI. Think about the key components and benefits.",
        enable_thinking=True,
        system_prompt="You are an AI expert. Show your reasoning process.",
        temperature=0.6
    )
    
    print("\n\n✨ Demo completed!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           QWEN3 THINKING MODE STREAM DEMO                    ║
║                                                              ║
║  This demo shows how thinking mode works with streaming:    ║
║  1. 💭 Thinking process is shown first                      ║
║  2. 💬 Then the final answer streams in real-time          ║
║  3. ⚡ Better user experience than waiting for full answer ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
        sys.exit(0)
