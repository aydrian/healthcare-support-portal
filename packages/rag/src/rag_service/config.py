import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Healthcare Support Portal - RAG Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = "0.0.0.0"
    port: int = 8003

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare"
    )

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_context_length: int = 8000
    similarity_threshold: float = 0.3
    max_results: int = 5

    # Oso Configuration
    oso_url: str = os.getenv("OSO_URL", "http://localhost:8080")
    oso_auth: str = os.getenv("OSO_AUTH", "e_0123456789_12345_osotesttoken01xiIn")

    class Config:
        env_file = ".env"

settings = Settings()
