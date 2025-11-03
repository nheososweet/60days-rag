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
        conversation_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate a streaming response from Gemini.
        
        Args:
            message: User message to send
            model: Model to use (defaults to config setting)
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            conversation_id: Conversation ID for context
            
        Yields:
            Dictionary chunks with text, done status, and conversation_id
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
            
            # Generate streaming response
            for chunk in self.client.models.generate_content_stream(
                model=model_name,
                contents=message,
                config=config
            ):
                if chunk.text:
                    yield {
                        "chunk": chunk.text,
                        "done": False,
                        "conversation_id": conversation_id
                    }
            
            # Send final done signal
            yield {
                "chunk": "",
                "done": True,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            # Send error in stream
            yield {
                "chunk": f"Error: {str(e)}",
                "done": True,
                "conversation_id": conversation_id,
                "error": True
            }
    
    def _extract_usage(self, response) -> Optional[Dict[str, int]]:
        """Extract token usage from response if available."""
        try:
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                return {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0)
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
