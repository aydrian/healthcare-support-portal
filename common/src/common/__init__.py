"""
Common package for Healthcare Support Portal
Shared models, database utilities, and policies
"""

from .models import Base, User, Patient, Document, Embedding
from .db import get_db, engine, SessionLocal
from .auth import get_current_user, create_access_token, verify_password

__all__ = [
    "Base",
    "User", 
    "Patient", 
    "Document", 
    "Embedding",
    "get_db",
    "engine",
    "SessionLocal",
    "get_current_user",
    "create_access_token",
    "verify_password",
]
