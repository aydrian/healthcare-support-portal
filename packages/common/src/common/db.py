import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to enable PostgreSQL extensions
def enable_extensions():
    """Enable required PostgreSQL extensions (pgvector for embeddings)"""
    try:
        with engine.begin() as conn:
            # Enable pgvector extension for vector similarity search
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            print("✅ PostgreSQL extensions enabled successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not enable extensions: {e}")
        # Don't raise the exception - let the service continue
        # Extensions might already be enabled or the database might not support them

# Function to create all tables
def create_tables():
    from .models import Base
    Base.metadata.create_all(bind=engine)

# Function to drop all tables (for testing)
def drop_tables():
    from .models import Base
    Base.metadata.drop_all(bind=engine)
