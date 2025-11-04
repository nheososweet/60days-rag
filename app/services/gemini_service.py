"""
Gemini AI service for chat and text generation with streaming support.
"""
import uuid
from typing import AsyncIterator, Optional, Dict, Any
from google import genai
from google.genai import types

from app.core.config import settings


class GeminiService:
    """Service for interacting with Google Gemini AI."""
    
    def __init__(self):
        """Initialize Gemini client."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.default_model = settings.DEFAULT_MODEL
        
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a non-streaming response from Gemini.
        
        Args:
            message: User message to send
            model: Model to use (defaults to config setting)
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            conversation_id: Conversation ID for context
            
        Returns:
            Dictionary with response, conversation_id, and metadata
        """
        model_name = model or self.default_model
        temp = temperature if temperature is not None else settings.TEMPERATURE
        max_tok = max_tokens or settings.MAX_TOKENS
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        try:
            # Configure generation
            config = types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
            
            # Generate response
            response = self.client.models.generate_content(
                model=model_name,
                contents=message,
                config=config
            )
            
            return {
                "response": response.text,
                "conversation_id": conversation_id,
                "model": model_name,
                "usage": self._extract_usage(response)
            }
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    async def generate_stream_response(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_instruction: Optional[str] = None,
        thinking_budget: Optional[int] = None,
        include_thoughts: bool = False,
        conversation_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate a streaming response from Gemini with thinking support.
        
        Args:
            message: User message to send
            model: Model to use (defaults to config setting)
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            system_instruction: System instruction for the model
            thinking_budget: Token budget for thinking (-1 for dynamic, 0 to disable)
            include_thoughts: Whether to include thought summaries in response
            conversation_id: Conversation ID for context
            
        Yields:
            Dictionary chunks with text/thought, done status, and metadata
        """
        model_name = model or self.default_model
        temp = temperature if temperature is not None else settings.TEMPERATURE
        max_tok = max_tokens or settings.MAX_TOKENS
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        try:
            # Configure thinking
            thinking_config = types.ThinkingConfig(
                thinking_budget=thinking_budget if thinking_budget is not None else 0,
                include_thoughts=include_thoughts
            )
            
            # Configure generation
            config = types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                thinking_config=thinking_config
            )
            
            # Add system instruction if provided
            if system_instruction:
                config.system_instruction = system_instruction
            
            thoughts_text = ""
            answer_text = ""
            
            # Generate streaming response
            for chunk in self.client.models.generate_content_stream(
                model=model_name,
                contents=message,
                config=config
            ):
                # Process each part in the chunk
                for part in chunk.candidates[0].content.parts:
                    if not part.text:
                        continue
                    
                    # Check if this is a thought or answer
                    if part.thought:
                        thoughts_text += part.text
                        yield {
                            "type": "thought",
                            "chunk": part.text,
                            "done": False,
                            "conversation_id": conversation_id
                        }
                    else:
                        answer_text += part.text
                        yield {
                            "type": "answer",
                            "chunk": part.text,
                            "done": False,
                            "conversation_id": conversation_id
                        }
            
            # Send final done signal with usage info
            usage_data = self._extract_usage_from_chunk(chunk) if 'chunk' in locals() else None
            yield {
                "type": "done",
                "chunk": "",
                "done": True,
                "conversation_id": conversation_id,
                "usage": usage_data,
                "has_thoughts": bool(thoughts_text)
            }
            
        except Exception as e:
            # Send error in stream
            yield {
                "type": "error",
                "chunk": f"Error: {str(e)}",
                "done": True,
                "conversation_id": conversation_id,
                "error": str(e)
            }
    
    def _extract_usage(self, response) -> Optional[Dict[str, int]]:
        """Extract token usage from response if available."""
        try:
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                return {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                    "thoughts_tokens": getattr(usage, 'thoughts_token_count', 0)
                }
        except:
            pass
        return None
    
    def _extract_usage_from_chunk(self, chunk) -> Optional[Dict[str, int]]:
        """Extract token usage from streaming chunk if available."""
        try:
            if hasattr(chunk, 'usage_metadata'):
                usage = chunk.usage_metadata
                return {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                    "thoughts_tokens": getattr(usage, 'thoughts_token_count', 0)
                }
        except:
            pass
        return None
    
    async def check_health(self) -> bool:
        """
        Check if Gemini API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.client.models.generate_content(
                model=self.default_model,
                contents="Hello",
                config=types.GenerateContentConfig(
                    max_output_tokens=10,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            return bool(response.text)
        except Exception:
            return False


# Global service instance
gemini_service = GeminiService()
