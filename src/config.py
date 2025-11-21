from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Uses pydantic-settings for type-safe configuration management
    with automatic loading from .env files.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "conversations"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: str | None = None
    
    # Memory System Configuration
    max_context_tokens: int = 3000
    memory_retrieval_limit: int = 5
    memory_relevance_threshold: float = 0.7
    window_size: int = 10
    
    # API Configuration
    api_title: str = "Dynamic Memory API"
    api_version: str = "1.0.0"
    debug: bool = False


# Global settings instance
settings = Settings()
