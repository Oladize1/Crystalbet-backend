from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

# Schema for returning user profile details
class UserProfile(BaseModel):
    id: str = Field(..., alias="_id")  # Using alias for MongoDB ObjectId
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True

# Schema for updating the user profile
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

# Schema for creating a new user
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True

# Schema for user login with either email or username
class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @validator("password")
    def require_username_or_email(cls, v, values):
        if not values.get("email") and not values.get("username"):
            raise ValueError("Either 'email' or 'username' must be provided.")
        return v

# Schema for returning user details in response
class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")  # Using alias for MongoDB ObjectId
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True

# Schema for returning authentication tokens
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for token data, to be included in the request/response of secured routes
class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# Schema for the user stored in the database
class UserInDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Using alias for MongoDB ObjectId
    email: EmailStr
    username: str
    hashed_password: str  # Renamed for clarity to distinguish from plain password
    created_at: datetime
    is_active: bool
    is_admin: bool  # Adjusted to be consistent with other schemas

    class Config:
        from_attributes = True
        populate_by_name = True
