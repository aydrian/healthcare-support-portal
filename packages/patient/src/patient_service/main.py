import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy_oso_cloud

from common.db import enable_extensions, create_tables
from common.models import User, Patient, Document, Base
from .config import settings
from .routers import patients

# Initialize SQLAlchemy Oso Cloud with registry and server settings
sqlalchemy_oso_cloud.init(
    Base.registry,
    url=settings.oso_server_url,
    api_key="e_0123456789_12345_osotesttoken01xiIn"
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Patient management service with role-based access control",
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
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])

@app.on_event("startup")
async def startup_event():
    """Enable extensions and create database tables on startup"""
    enable_extensions()
    create_tables()
    print(f"🚀 {settings.app_name} started on port {settings.port}")

@app.get("/")
async def root():
    return {
        "service": "patient_service",
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Make Oso Cloud instance available to routes
app.state.oso_sqlalchemy = sqlalchemy_oso_cloud
