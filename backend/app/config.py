import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "The Lenny Growth Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    # Database Configuration (PostgreSQL primary with auto fallback for smoke-testing)
    DATABASE_URL: str = "sqlite+aiosqlite:///./lenny_growth.db"
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_MAX_OVERFLOW: int = 20

    # Model Configuration
    DEFAULT_PROVIDER: str = "ollama"  # ollama | anthropic | openai
    
    # Ollama Local LLM Configuration (Mandatory Demo)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TIMEOUT_SECONDS: float = 180.0

    # Anthropic Claude SDK Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    # Groq Cloud API Configuration (Ultra-fast GPT OSS 120B / Qwen)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # Hybrid RAG & Ingestion Configuration
    RAG_TOP_K: int = 5
    RRF_K: int = 60
    TRANSCRIPTS_DIR: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "rag", "data", "lenny_transcripts"
    )
    MANIFEST_PATH: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "rag", "data", "source_manifest.json"
    )

    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            "../.env",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
