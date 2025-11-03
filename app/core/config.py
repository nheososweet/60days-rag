"""
Configuration management for the application.
Loads settings from environment variables and provides typed config objects.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    APP_NAME: str = "60days-rag"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Google Gemini API
    GEMINI_API_KEY: str
    
    # LangChain Settings
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "60days-rag"
    
    # Vector Database Settings
    VECTOR_DB_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # Model Settings
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to create a singleton pattern.
    """
    return Settings()


# Create a global settings instance
settings = get_settings()
