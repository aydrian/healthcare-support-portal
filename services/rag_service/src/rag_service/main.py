import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oso import Oso
from sqlalchemy_oso import SQLAlchemyOso
import openai

from common.db import create_tables
from common.models import User, Patient, Document
from .config import settings
from .routers import documents, chat

# Set OpenAI API key
openai.api_key = settings.openai_api_key

# Initialize Oso
oso = Oso()
oso.register_class(User)
oso.register_class(Patient) 
oso.register_class(Document)
oso.load_file(settings.policy_path)

# Initialize SQLAlchemy Oso
sqlalchemy_oso = SQLAlchemyOso(oso)
sqlalchemy_oso.register_models([User, Patient, Document])

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="RAG service with vector search and AI-powered responses",
    version="0.1.0",
    debug=settings.debug
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
    """Create database tables on startup"""
    create_tables()
    print(f"🚀 {settings.app_name} started on port {settings.port}")

@app.get("/")
async def root():
    return {
        "service": "rag_service",
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Make oso and settings available to routes
app.state.oso = oso
app.state.settings = settings
