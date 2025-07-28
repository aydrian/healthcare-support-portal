from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from common.db import get_db
from common.models import User
from common.auth import get_current_user
from common.schemas import UserResponse, UserCreate

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
    oso = request.app.state.oso

    # Use Oso to filter users the current user can read
    authorized_query = oso.authorized_query(current_user, "read", User, session=db)
    users = authorized_query.offset(skip).limit(limit).all()

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
    oso = request.app.state.oso

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if current user is authorized to read this user
    if not oso.is_allowed(current_user, "read", user):
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
    oso = request.app.state.oso

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if current user is authorized to write this user
    if not oso.is_allowed(current_user, "write", user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Update user fields
    user.username = user_update.username
    user.email = user_update.email
    user.role = user_update.role
    user.department = user_update.department

    db.commit()
    db.refresh(user)

    return user
