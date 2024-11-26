from fastapi import HTTPException, status, Depends
from bson import ObjectId
import logging
from core.security import hash_password, verify_password, create_access_token, create_reset_token
from db.mongodb import get_db
from core.config import settings
from utils.jwt import decode_token, oauth2_scheme
from models.user import UserInDB
from schemas.auth import UserCreate, UserUpdate
from datetime import datetime, timedelta
from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema

logger = logging.getLogger(__name__)

# Helper function for raising HTTPExceptions with logging
def raise_http_exception(status_code, detail):
    logger.error(f"HTTPException: {status_code} - {detail}")
    raise HTTPException(status_code=status_code, detail=detail)

# Create a new user
async def create_user(db, user: UserCreate):
    logger.info(f"Creating user with email: {user.email} and username: {user.username}")

    # Check if the email or username is already registered
    existing_user = await db["users"].find_one({"$or": [{"email": user.email}, {"username": user.username}]})
    if existing_user:
        raise_http_exception(status.HTTP_400_BAD_REQUEST, "Email or username is already registered.")

    # Hash the password and create user data
    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "is_superuser": False,
    }

    # Insert user data into the database and return the user
    try:
        result = await db["users"].insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return UserInDB(**user_data)
    except Exception as e:
        logger.error(f"Error inserting user: {e}")
        raise_http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database insertion error")

# Authenticate user by either email or username and password
async def authenticate_user(db, identifier: str, password: str):
    # Check for user by either email or username
    user = await db["users"].find_one({"$or": [{"email": identifier}, {"username": identifier}]})
    if user:
        if verify_password(password, user["hashed_password"]):
            logger.info(f"User authenticated: {identifier}")
            return UserInDB(**user)
        else:
            raise_http_exception(status.HTTP_401_UNAUTHORIZED, "Incorrect password.")
    else:
        raise_http_exception(status.HTTP_404_NOT_FOUND, "User not found with provided email or username.")

# Send password reset email
async def send_reset_password_email(email: EmailStr, db):
    user = await db["users"].find_one({"email": email})
    if not user:
        raise_http_exception(status.HTTP_404_NOT_FOUND, "User with this email not found.")

    token = create_reset_token({"email": email})
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the link to reset your password: {reset_link}",
        subtype="html"
    )

    try:
        fm = FastMail(settings.mail_config)
        await fm.send_message(message)
        await db["users"].update_one(
            {"email": email},
            {"$set": {"reset_token": token, "reset_token_expiration": datetime.utcnow() + timedelta(hours=1)}}
        )
        logger.info(f"Password reset email sent to: {email}")
    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")
        raise_http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to send reset email.")

# Reset password
async def reset_password(db, reset_token: str, new_password: str):
    user = await db["users"].find_one({"reset_token": reset_token})
    if not user:
        raise_http_exception(status.HTTP_404_NOT_FOUND, "Invalid reset token.")
    
    if user["reset_token_expiration"] < datetime.utcnow():
        raise_http_exception(status.HTTP_400_BAD_REQUEST, "Reset token has expired.")
    
    hashed_password = hash_password(new_password)
    await db["users"].update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"hashed_password": hashed_password, "reset_token": None, "reset_token_expiration": None}}
    )
    logger.info(f"Password reset for user ID: {user['_id']}")

# Get user by email
async def get_user_by_email(db, email: EmailStr):
    user = await db["users"].find_one({"email": email})
    if user:
        return UserInDB(**user)
    raise_http_exception(status.HTTP_404_NOT_FOUND, "User not found.")

# Update user details
async def update_user(db, user_update: UserUpdate, user_id: str):
    if not ObjectId.is_valid(user_id):
        raise_http_exception(status.HTTP_400_BAD_REQUEST, "Invalid user ID.")
    
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise_http_exception(status.HTTP_404_NOT_FOUND, "User not found.")
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    
    await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    logger.info(f"User updated: {user_id}")
    return UserInDB(**updated_user)

# Verify admin privileges
async def verify_admin(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    user_info = decode_token(token)
    user = await db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    if not user:
        raise_http_exception(status.HTTP_404_NOT_FOUND, "User not found.")
    if not user.get("is_superuser", False):
        raise_http_exception(status.HTTP_403_FORBIDDEN, "Admin privileges required.")
    return UserInDB(**user)

# Get current authenticated user
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        user_info = decode_token(token)
        user_id = user_info.get("sub")
        if not user_id:
            raise_http_exception(status.HTTP_400_BAD_REQUEST, "Invalid token data.")
        
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            raise_http_exception(status.HTTP_404_NOT_FOUND, "User not found.")
        
        return UserInDB(**user)
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise_http_exception(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token.")
