"""
LLM Configuration Management
Centralized configuration for AI/ML models
"""
from pydantic_settings import BaseSettings
from typing import Optional, Literal
from functools import lru_cache


class LLMSettings(BaseSettings):
    # LLM Provider Selection (Only OpenAI and Groq)
    LLM_PROVIDER: Literal["openai", "groq"] = "groq"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # Groq Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_TEMPERATURE: float = 1.0
    GROQ_MAX_TOKENS: int = 8192
    GROQ_TOP_P: float = 1.0
    
    # Agent Configuration
    AGENT_NAME: str = "Help Desk Agent"
    AGENT_VERSION: str = "1.0.0"
    AGENT_DESCRIPTION: str = "Banking IT Help Desk Assistant powered by AI"
    
    # LLM Feature Flags
    LLM_ENABLE_TICKET_ANALYSIS: bool = True
    LLM_ENABLE_AUTO_RESPONSE: bool = True
    LLM_ENABLE_SENTIMENT_ANALYSIS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env (like app configs)
    
    def get_active_provider_config(self) -> dict:
        """Get configuration for the active LLM provider"""
        if self.LLM_PROVIDER == "openai":
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "temperature": self.OPENAI_TEMPERATURE,
                "max_tokens": self.OPENAI_MAX_TOKENS,
                "agent_name": self.AGENT_NAME
            }
        elif self.LLM_PROVIDER == "groq":
            return {
                "provider": "groq",
                "api_key": self.GROQ_API_KEY,
                "model": self.GROQ_MODEL,
                "temperature": self.GROQ_TEMPERATURE,
                "max_tokens": self.GROQ_MAX_TOKENS,
                "top_p": self.GROQ_TOP_P,
                "agent_name": self.AGENT_NAME
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {self.LLM_PROVIDER}")
    
    def is_provider_configured(self) -> bool:
        """Check if the selected provider is properly configured"""
        if self.LLM_PROVIDER == "openai":
            return bool(self.OPENAI_API_KEY)
        elif self.LLM_PROVIDER == "groq":
            return bool(self.GROQ_API_KEY)
        return False


@lru_cache()
def get_llm_settings() -> LLMSettings:
    """Get cached LLM settings instance"""
    return LLMSettings()


llm_settings = get_llm_settings()
