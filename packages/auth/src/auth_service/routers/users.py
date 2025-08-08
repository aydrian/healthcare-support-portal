from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy_oso_cloud import authorized, get_oso

from common.db import get_db
from common.models import User
from common.auth import get_current_user
from common.schemas import UserResponse, UserCreate
from common.auth import get_password_hash
from common.oso_sync import sync_user_role_change, sync_department_change, sync_admin_global_access

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def list_users(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List users (with Oso authorization)
    """
    # Use Oso Cloud to filter users the current user can read
    users = db.query(User).options(authorized(current_user, "read", User)).offset(skip).limit(limit).all()

    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific user (with Oso authorization)
    """
    oso = get_oso()

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if current user is authorized to read this user
    if not oso.authorize(current_user, "read", user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )

    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user (with Oso authorization)
    """
    oso = get_oso()

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if current user is authorized to write this user
    if not oso.authorize(current_user, "write", user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Track changes for OSO sync
    old_role = user.role
    old_department = user.department
    
    # Update user fields
    user.username = user_update.username
    user.email = user_update.email
    user.role = user_update.role
    user.department = user_update.department

    db.commit()
    db.refresh(user)
    
    # Sync OSO facts if role or department changed
    try:
        if old_role != user.role:
            sync_user_role_change(user, old_role)
        
        if old_department != user.department:
            sync_department_change(user, old_department)
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to sync OSO facts for user {user.id}: {e}")

    return user

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new user (admin only)
    """
    oso = get_oso()
    
    # Check if current user has admin role (only admins can create users)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create new users"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | 
        (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        department=user_data.department,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Sync OSO facts for new user
    try:
        if new_user.role == "admin":
            sync_admin_global_access(new_user)
        print(f"Synced OSO facts for new user {new_user.username}")
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to sync OSO facts for new user {new_user.id}: {e}")
    
    return new_user
