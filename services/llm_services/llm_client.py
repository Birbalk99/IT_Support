"""
LLM Client
Universal client for different LLM providers (OpenAI)
Note: Groq is handled separately in services/groq_service.py
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from core.llm_config import llm_settings
from core.logging.logger import agent_logger


class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def analyze_text(self, text: str, task: str) -> Dict[str, Any]:
        """Analyze text for specific task"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client"""
    
    def __init__(self):
        self.api_key = llm_settings.OPENAI_API_KEY
        self.model = llm_settings.OPENAI_MODEL
        self.temperature = llm_settings.OPENAI_TEMPERATURE
        self.max_tokens = llm_settings.OPENAI_MAX_TOKENS
        
        agent_logger.info(
            f"OpenAI client initialized with model: {self.model}",
            method="INIT"
        )
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            # TODO: Implement actual OpenAI API call
            # from openai import AsyncOpenAI
            # client = AsyncOpenAI(api_key=self.api_key)
            # response = await client.chat.completions.create(...)
            
            agent_logger.info("Generating OpenAI response", method="GENERATE")
            
            # Placeholder response
            return "OpenAI response placeholder - Implement actual API call"
            
        except Exception as e:
            agent_logger.error(f"OpenAI error: {str(e)}", method="GENERATE")
            raise
    
    async def analyze_text(self, text: str, task: str) -> Dict[str, Any]:
        """Analyze text using OpenAI"""
        # TODO: Implement text analysis
        return {"task": task, "result": "placeholder"}


class LLMClientFactory:
    """Factory to create appropriate LLM client"""
    
    @staticmethod
    def create_client() -> BaseLLMClient:
        """Create LLM client based on configuration"""
        provider = llm_settings.LLM_PROVIDER
        
        if not llm_settings.is_provider_configured():
            agent_logger.warning(
                f"LLM provider '{provider}' not properly configured",
                method="FACTORY"
            )
            raise ValueError(f"LLM provider '{provider}' is not properly configured")
        
        clients = {
            "openai": OpenAIClient
        }
        
        client_class = clients.get(provider)
        if not client_class:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        agent_logger.info(f"Creating LLM client for provider: {provider}", method="FACTORY")
        return client_class()


# Global LLM client instance
def get_llm_client() -> Optional[BaseLLMClient]:
    """
    Get LLM client instance
    Returns None if not configured or if using Groq (handled separately)
    """
    try:
        if llm_settings.LLM_PROVIDER == "groq":
            return None  # Groq is handled by groq_service
        return LLMClientFactory.create_client()
    except Exception as e:
        agent_logger.warning(f"Could not create LLM client: {str(e)}", method="GET_CLIENT")
        return None
