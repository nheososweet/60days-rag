"""
Qwen3 AI Service - Local model integration using vLLM.

Service này dùng để giao tiếp với Qwen3-0.6B model đang chạy local qua vLLM.
vLLM cung cấp OpenAI-compatible API, nên chúng ta dùng format tương tự OpenAI.

Key concepts:
- vLLM: Server để chạy LLM models nhanh và efficient
- OpenAI-compatible API: API giống như OpenAI, dễ sử dụng
- Streaming: Gửi response từng chunk thay vì đợi hết
- Thinking Mode: Qwen3 có thể show reasoning process trong <think> tags
- httpx: Async HTTP client cho Python
"""

import uuid
import json
import logging
from typing import AsyncIterator, Optional, Dict, Any, List, AsyncGenerator
import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class QwenService:
    """
    Service để tương tác với Qwen3 model qua vLLM server.
    
    Qwen3-0.6B là một model nhỏ (600M parameters) chạy local,
    phù hợp để học và thử nghiệm RAG.
    
    Features:
    - Non-streaming và streaming response
    - Thinking mode support (parse <think> tags)
    - Configurable generation parameters
    - RAG-ready (context injection)
    
    Attributes:
        base_url: URL của vLLM server
        model_name: Tên model đang chạy
        timeout: Request timeout (300s cho long responses)
    """
    
    def __init__(self):
        """
        Khởi tạo Qwen service với thinking mode support.
        """
        # VLLM server URL (có thể running trên WSL hoặc local)
        self.base_url = settings.QWEN_BASE_URL  # http://localhost:8000
        self.model_name = settings.QWEN_MODEL   # Qwen/Qwen3-0.6B
        self.timeout = 300  # 5 minutes timeout cho long responses
        
        # Default generation parameters cho thinking mode
        # Thinking mode: Model suy nghĩ trước khi trả lời
        self.thinking_params = {
            "temperature": 0.6,      # Thấp hơn = consistent reasoning
            "top_p": 0.95,           # Nucleus sampling
            "top_k": 20,             # Top-k sampling
            "max_tokens": 32768,     # Max context của Qwen3
            "presence_penalty": 1.5  # Giảm repetition
        }
        
        # Parameters cho non-thinking mode
        # Non-thinking: Trả lời trực tiếp không cần suy nghĩ
        self.non_thinking_params = {
            "temperature": 0.7,      # Cao hơn = creative hơn
            "top_p": 0.8,
            "top_k": 20,
            "max_tokens": 32768,
            "presence_penalty": 1.5
        }
        
        logger.info(f"Qwen service initialized with model: {self.model_name}")
    
    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        enable_thinking: bool = True,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Make request to VLLM server.
        
        Internal helper method để gọi vLLM API.
        
        Args:
            messages: List of message dicts với role và content
            enable_thinking: Có enable thinking mode không
            stream: Có stream response không
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Response data hoặc streaming response object
        """
        
        # Choose parameters based on thinking mode
        # Thinking mode dùng temperature thấp hơn để reasoning consistent
        params = self.thinking_params if enable_thinking else self.non_thinking_params
        params.update(kwargs)  # Override với user-provided params
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            **params
        }
        
        # Add thinking control via extra_body
        # vLLM support extra_body để pass custom parameters
        if enable_thinking is not None:
            payload["extra_body"] = {
                "enable_thinking": enable_thinking
            }
        
        try:
            # Create client với timeout
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                if stream:
                    return response
                else:
                    return response.json()
                    
        except httpx.RequestError as e:
            logger.error(f"Request error to Qwen server: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Qwen server: {str(e)}"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Qwen server: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Qwen server error: {e.response.text}"
            )
    
    async def generate_response(
        self,
        message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        enable_thinking: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a single response from Qwen model (NON-STREAMING).
        
        Args:
            message: User question/prompt
            temperature: Generation temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            conversation_id: Conversation ID for tracking
            system_prompt: System instruction for model
            context: Optional context from RAG retrieval
            enable_thinking: Whether to enable thinking mode
            
        Returns:
            Dict with:
            - response: Final answer text (without <think> tags)
            - thinking_content: Thinking process (if enable_thinking=True)
            - conversation_id: Conversation ID
            - model: Model name
            - usage: Token usage statistics
            - enable_thinking: Whether thinking was enabled
            
        Example:
            >>> result = await qwen_service.generate_response(
            ...     message="What is 2+2?",
            ...     enable_thinking=True,
            ...     system_prompt="You are a math tutor"
            ... )
            >>> print(result["thinking_content"])  # See reasoning
            >>> print(result["response"])  # Get answer
        """
        
        # Generate conversation ID nếu chưa có
        if not conversation_id:
            conversation_id = f"qwen_conv_{uuid.uuid4().hex[:12]}"
        
        # Build messages array
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context if provided (for RAG)
        # Context được inject vào user message
        if context:
            user_content = f"""Context information:
{context}

Question: {message}

Please answer the question based on the provided context."""
        else:
            user_content = message
            
        messages.append({"role": "user", "content": user_content})
        
        # Make request
        response = await self._make_request(
            messages=messages,
            enable_thinking=enable_thinking,
            stream=False,
            temperature=temperature or settings.TEMPERATURE,
            max_tokens=max_tokens or settings.MAX_TOKENS
        )
        
        # Parse response
        if response.get("choices") and len(response["choices"]) > 0:
            choice = response["choices"][0]
            content = choice.get("message", {}).get("content", "")
            
            # Parse thinking content if available
            # Thinking format: <think>reasoning here</think>actual answer
            thinking_content = ""
            final_content = content
            
            if enable_thinking and "<think>" in content:
                # Extract thinking content
                think_start = content.find("<think>")
                think_end = content.find("</think>")
                
                if think_start != -1 and think_end != -1:
                    # Extract thinking process
                    thinking_content = content[think_start + 7:think_end].strip()
                    # Extract final answer (after </think> tag)
                    final_content = content[think_end + 8:].strip()
            
            return {
                "response": final_content,  # API expects 'response' key
                "thinking_content": thinking_content,
                "conversation_id": conversation_id,
                "model": self.model_name,
                "enable_thinking": enable_thinking,
                "usage": response.get("usage", {})
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No response content from Qwen model"
            )
    
    async def generate_stream_response(
        self,
        message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        enable_thinking: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate STREAMING response from Qwen model.
        
        Streaming với thinking mode support:
        - Nếu enable_thinking=True, sẽ yield thinking content trước
        - Sau đó yield final answer từng chunk
        - Parse <think> tags trong real-time
        
        Args:
            message: User question/prompt
            temperature: Generation temperature
            max_tokens: Max tokens in response
            conversation_id: Conversation ID
            system_prompt: System instruction
            context: Optional RAG context
            enable_thinking: Enable thinking mode
            
        Yields:
            Dict chunks with:
            - type: 'thinking' | 'content' | 'finish' | 'error'
            - content: Text content
            - thinking_content: Thinking process (if type='thinking')
            - chunk: Text chunk (for API compatibility)
            - done: Boolean indicating completion
            - conversation_id: Conversation ID
            
        Example:
            >>> async for chunk in qwen_service.generate_stream_response(
            ...     message="Explain RAG",
            ...     enable_thinking=True
            ... ):
            ...     if chunk["type"] == "thinking":
            ...         print("Thinking:", chunk["thinking_content"])
            ...     elif chunk["type"] == "content":
            ...         print(chunk["content"], end="", flush=True)
        """
        print(f"Starting streaming response (thinking={enable_thinking})...")
        # Generate conversation ID
        if not conversation_id:
            conversation_id = f"qwen_conv_{uuid.uuid4().hex[:12]}"
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context if provided
        if context:
            user_content = f"""Context information:
{context}

Question: {message}

Please answer the question based on the provided context."""
        else:
            user_content = message
            
        messages.append({"role": "user", "content": user_content})
        
        # Make streaming request
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare request
                params = self.thinking_params if enable_thinking else self.non_thinking_params
                
                # Override với user params
                if temperature is not None:
                    params["temperature"] = temperature
                if max_tokens is not None:
                    params["max_tokens"] = max_tokens
                
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "stream": True,
                    **params
                }
                
                # Add thinking control
                if enable_thinking is not None:
                    payload["extra_body"] = {
                        "enable_thinking": enable_thinking
                    }
                
                # Stream response
                async with client.stream(
                    "POST",
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    
                    # Buffers để parse thinking content
                    thinking_buffer = ""
                    in_thinking = False
                    thinking_sent = False
                    
                    # Iterate through SSE stream
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data.strip() == "[DONE]":
                                # Send final done signal
                                yield {
                                    "chunk": "",
                                    "done": True,
                                    "conversation_id": conversation_id
                                }
                                break
                            
                            try:
                                chunk = json.loads(data)
                                
                                if chunk.get("choices") and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        # Handle thinking content parsing
                                        if enable_thinking:
                                            # Check for <think> tag
                                            if "<think>" in content and not in_thinking:
                                                in_thinking = True
                                                # Bỏ phần trước <think>
                                                content = content.split("<think>", 1)[-1]
                                            
                                            # Check for </think> tag
                                            if in_thinking and "</think>" in content:
                                                # Split at </think>
                                                think_part, rest_content = content.split("</think>", 1)
                                                thinking_buffer += think_part
                                                
                                                # Send thinking content (once)
                                                if not thinking_sent and thinking_buffer.strip():
                                                    yield {
                                                        "type": "thinking",
                                                        "thinking_content": thinking_buffer.strip(),
                                                        "chunk": "",  # For API compatibility
                                                        "done": False,
                                                        "conversation_id": conversation_id
                                                    }
                                                    thinking_sent = True
                                                
                                                in_thinking = False
                                                content = rest_content
                                            elif in_thinking:
                                                # Still in thinking mode, buffer it
                                                thinking_buffer += content
                                                continue
                                        
                                        # Send regular content chunk
                                        if content:
                                            yield {
                                                "type": "content",
                                                "chunk": content,  # For API compatibility
                                                "done": False,
                                                "conversation_id": conversation_id
                                            }
                                    
                                    # Handle finish reason
                                    finish_reason = chunk["choices"][0].get("finish_reason")
                                    if finish_reason:
                                        yield {
                                            "type": "finish",
                                            "finish_reason": finish_reason,
                                            "chunk": "",
                                            "done": True,
                                            "conversation_id": conversation_id
                                        }
                                        
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.RequestError as e:
            logger.error(f"Streaming request error: {e}")
            yield {
                "type": "error",
                "chunk": f"Connection error: {str(e)}",
                "done": True,
                "error": True,
                "conversation_id": conversation_id
            }
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "type": "error", 
                "chunk": f"Streaming error: {str(e)}",
                "done": True,
                "error": True,
                "conversation_id": conversation_id
            }
    
    async def check_health(self) -> bool:
        """
        Check if Qwen vLLM server is available.
        
        Returns:
            True if server accessible, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """
        Close HTTP connections (for cleanup).
        Note: AsyncClient is created per-request, so nothing to close here.
        """
        pass


# Global service instance
# Tạo một instance duy nhất để reuse trong toàn bộ app
# Pattern: Singleton
qwen_service = QwenService()
