"""
Configuration Management
Centralized configuration for the application
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "IT Help Desk Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "d87cc423ad4045ae85020d2e2e1c2f126145701771d521e152d53533041a4691"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security Features - Can be enabled/disabled
    ENABLE_USER_ID_VALIDATION: bool = True  # Set to False to disable user ID requirement
    ENABLE_URL_WHITELIST: bool = True  # Set to False to disable URL whitelist
    
    # Allowed Origins for CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://localhost:3000",
        "*"  # Allow all origins
        # Add your React app URLs here
    ]
    
    # Allowed URLs/Endpoints (Whitelist)
    ALLOWED_ENDPOINTS: List[str] = [
        "/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/llm/query",
        "/api/auth/login",
        "/api/auth/register",
        # Add more allowed endpoints as needed
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Database
    DATABASE_URL: str = "sqlite:///./it_helpdesk.db"  # Change to PostgreSQL/MySQL in production
    
    # Logging
    LOG_RETENTION_DAYS: int = 10
    LOG_LEVEL: str = "INFO"
    
    # Redis (for caching and rate limiting)
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env (like LLM configs)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
