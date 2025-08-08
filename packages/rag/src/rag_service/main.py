import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

import openai
import sqlalchemy_oso_cloud
from common.migration_check import require_migrations_current
from common.models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import chat, documents

# Set OpenAI API key
openai.api_key = settings.openai_api_key

# Initialize SQLAlchemy Oso Cloud with registry and server settings
sqlalchemy_oso_cloud.init(
    Base.registry, url=settings.oso_url, api_key=settings.oso_auth
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="RAG service with vector search and AI-powered responses",
    version="0.1.0",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


@app.on_event("startup")
async def startup_event():
    """Verify migrations and start service"""
    # Verify database migrations are current
    require_migrations_current()
    print(f"🚀 {settings.app_name} started on port {settings.port}")


@app.get("/")
async def root():
    return {"service": "rag_service", "status": "healthy", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Make Oso Cloud instance and settings available to routes
app.state.oso_sqlalchemy = sqlalchemy_oso_cloud
app.state.settings = settings
