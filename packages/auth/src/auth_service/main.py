from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy_oso_cloud

from common.db import enable_extensions
from common.models import Base, User, Patient, Document
from .config import settings
from .routers import auth, users

# Initialize SQLAlchemy Oso Cloud with registry and server settings
sqlalchemy_oso_cloud.init(
    Base.registry,
    url=settings.oso_server_url,
    api_key="e_0123456789_12345_osotesttoken01xiIn"
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Authentication and user management service",
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    """Enable extensions on startup"""
    enable_extensions()
    print(f"🚀 {settings.app_name} started on port {settings.port}")

@app.get("/")
async def root():
    return {
        "service": "auth_service",
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Make Oso Cloud instance available to routes
app.state.oso_sqlalchemy = sqlalchemy_oso_cloud
