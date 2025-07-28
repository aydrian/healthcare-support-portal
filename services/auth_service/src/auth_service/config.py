import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Healthcare Support Portal - Auth Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = "0.0.0.0"
    port: int = 8001

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare"
    )

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = 30

    # Oso
    policy_path: str = "../../common/src/common/policies/authorization.polar"

    class Config:
        env_file = ".env"

settings = Settings()
