from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from core.security import get_current_user
from schemas.user import UserUpdate, UserResponse, UserInDB
from services.auth import get_user_by_email, update_user
from db.mongodb import get_db
from pymongo.collection import Collection

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile.
    Requires the user to be authenticated (JWT token).
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Collection = Depends(get_db)
):
    """
    Update the currently logged-in user's profile information.
    Fields such as name, email, etc., can be updated.
    Requires the user to be authenticated.
    """
    # Check if email is being updated and if the new email is already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The email is already registered to another user."
            )

    # Update the user information in MongoDB
    updated_user = update_user(db, user_update=user_update, user_id=current_user.id)
    return updated_user


@router.get("/", response_model=List[UserResponse])
def list_all_users(skip: int = 0, limit: int = 10, db: Collection = Depends(get_db)):
    """
    List all users with pagination.
    Requires admin access.
    """
    users = db.find().skip(skip).limit(limit)
    return list(users)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, db: Collection = Depends(get_db)):
    """
    Get user details by user ID.
    Requires admin access.
    """
    user = db.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Collection = Depends(get_db)):
    """
    Delete a user by ID.
    Requires admin access.
    """
    user = db.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete_one({"_id": user_id})
    return {"detail": "User deleted successfully"}
