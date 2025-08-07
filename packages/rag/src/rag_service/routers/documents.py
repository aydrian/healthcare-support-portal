import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy_oso_cloud import authorized, get_oso

from common.db import get_db
from common.models import User, Document
from common.auth import get_current_user
from common.schemas import DocumentResponse, DocumentCreate

from ..utils.text_processing import clean_text, chunk_text
from ..utils.embeddings import store_document_embeddings

router = APIRouter()

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    document_type: Optional[str] = Query(None),
    department: Optional[str] = Query(None)
):
    """
    List documents with Oso authorization filtering
    """
    # Use Oso Cloud to filter documents the current user can read
    query = db.query(Document).options(*authorized(current_user, "read", Document))

    # Apply optional filters
    if document_type:
        query = query.filter(Document.document_type == document_type)

    if department:
        query = query.filter(Document.department == department)

    # Apply pagination
    documents = query.offset(skip).limit(limit).all()

    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific document with Oso authorization
    """
    oso = get_oso()

    # Get the document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if current user is authorized to read this document
    if not oso.authorize(current_user, "read", document):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this document"
        )

    return document

@router.post("/", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document with embeddings
    """
    settings = request.app.state.settings

    # Check authorization - only doctors and admins can create documents
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create documents"
        )

    # Clean and process content
    cleaned_content = clean_text(document_data.content)

    # Create document
    db_document = Document(
        title=document_data.title,
        content=cleaned_content,
        document_type=document_data.document_type,
        patient_id=document_data.patient_id,
        department=document_data.department,
        created_by_id=current_user.id,
        is_sensitive=document_data.is_sensitive
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Generate and store embeddings
    chunks = chunk_text(
        cleaned_content, 
        chunk_size=settings.chunk_size, 
        chunk_overlap=settings.chunk_overlap
    )

    embedding_success = await store_document_embeddings(
        db_document, chunks, db, settings.embedding_model
    )

    if not embedding_success:
        print(f"Warning: Failed to generate embeddings for document {db_document.id}")

    return db_document

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str,
    document_type: str,
    department: Optional[str] = None,
    patient_id: Optional[int] = None,
    is_sensitive: bool = False,
    file: UploadFile = File(...),
    request: Request = Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document file
    """
    settings = request.app.state.settings

    # Check authorization
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents"
        )

    # Read file content
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )

    # Clean and process content
    cleaned_content = clean_text(content_str)

    # Create document
    db_document = Document(
        title=title,
        content=cleaned_content,
        document_type=document_type,
        patient_id=patient_id,
        department=department,
        created_by_id=current_user.id,
        is_sensitive=is_sensitive
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Generate and store embeddings
    chunks = chunk_text(
        cleaned_content,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    embedding_success = await store_document_embeddings(
        db_document, chunks, db, settings.embedding_model
    )

    if not embedding_success:
        print(f"Warning: Failed to generate embeddings for document {db_document.id}")

    return db_document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete document (admin only)
    """
    oso = get_oso()

    # Get the document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if current user is authorized to write this document
    if not oso.authorize(current_user, "write", document):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this document"
        )

    # Delete document and its embeddings (cascade)
    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
