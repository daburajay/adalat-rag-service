"""
app/services/llm_gateway.py - LLM Gateway (Gemini + Groq)
"""

import os
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMProviderError, MissingAPIKeyError

logger = get_logger(__name__)


class LLMGateway:
    """
    LLM Gateway with Gemini as primary and Groq as fallback.
    
    This class handles all LLM interactions with automatic fallback.
    If Gemini fails, it automatically switches to Groq.
    """
    
    def __init__(self):
        """Initialize LLM clients."""
        self._gemini_client = None
        self._groq_client = None
        self._gemini_available = False
        self._groq_available = False
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize both LLM clients."""
        # Initialize Gemini
        try:
            if settings.GEMINI_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._gemini_client = genai.GenerativeModel('gemini-1.5-flash')
                self._gemini_available = True
                logger.info("✅ Gemini initialized successfully")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found")
        except Exception as e:
            logger.warning(f"⚠️ Gemini initialization failed: {e}")
        
        # Initialize Groq (Fallback)
        try:
            if settings.GROQ_API_KEY:
                from groq import Groq
                self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self._groq_available = True
                logger.info("✅ Groq initialized successfully")
            else:
                logger.warning("⚠️ GROQ_API_KEY not found")
        except Exception as e:
            logger.warning(f"⚠️ Groq initialization failed: {e}")
        
        # Check if any LLM is available
        if not self._gemini_available and not self._groq_available:
            logger.error("❌ No LLM services available! Please check API keys.")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using available LLM.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_prompt: Optional system prompt for context
        
        Returns:
            Dictionary with response and metadata
        """
        # Prepare the prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Try Gemini first
        if self._gemini_available:
            try:
                logger.info("🤖 Using Gemini for generation")
                response = self._gemini_client.generate_content(
                    full_prompt,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                return {
                    "success": True,
                    "provider": "Gemini",
                    "response": response.text,
                    "usage": {
                        "prompt_tokens": getattr(response, 'usage_metadata', {}).get('prompt_token_count', 0),
                        "completion_tokens": getattr(response, 'usage_metadata', {}).get('candidates_token_count', 0),
                    }
                }
            except Exception as e:
                logger.warning(f"⚠️ Gemini failed: {e}, falling back to Groq")
        
        # Fallback to Groq
        if self._groq_available:
            try:
                logger.info("🤖 Using Groq as fallback")
                messages = [{"role": "user", "content": full_prompt}]
                
                response = self._groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return {
                    "success": True,
                    "provider": "Groq",
                    "response": response.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                    }
                }
            except Exception as e:
                logger.error(f"❌ Groq also failed: {e}")
                raise LLMProviderError("Groq", str(e))
        
        raise MissingAPIKeyError("No LLM API keys available")
    
    def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """
        Generate a streaming response.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_prompt: Optional system prompt
        
        Yields:
            Chunks of generated text
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Try Gemini streaming first
        if self._gemini_available:
            try:
                logger.info("🤖 Using Gemini streaming")
                response = self._gemini_client.generate_content(
                    full_prompt,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    },
                    stream=True
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                logger.warning(f"⚠️ Gemini streaming failed: {e}, falling back to Groq")
        
        # Fallback to Groq (non-streaming for now)
        if self._groq_available:
            try:
                logger.info("🤖 Using Groq")
                response = self._groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                yield response.choices[0].message.content
            except Exception as e:
                logger.error(f"❌ Groq failed: {e}")
                raise LLMProviderError("Groq", str(e))
        
        raise MissingAPIKeyError("No LLM API keys available")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers."""
        providers = []
        if self._gemini_available:
            providers.append("Gemini")
        if self._groq_available:
            providers.append("Groq")
        return providers
    
    def is_available(self) -> bool:
        """Check if any LLM is available."""
        return self._gemini_available or self._groq_available