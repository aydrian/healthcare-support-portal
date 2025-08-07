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
    similarity_threshold: float = 0.7
    max_results: int = 5

    # Oso Dev Server
    oso_server_url: str = os.getenv("OSO_SERVER_URL", "http://oso:8080")

    class Config:
        env_file = ".env"

settings = Settings()
