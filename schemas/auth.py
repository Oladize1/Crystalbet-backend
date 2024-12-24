from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

# Schema for user creation
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    class Config:
        from_attributes = True

# Schema for user update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
    password: Optional[str] = None  # Include password if the user can update it

    class Config:
        from_attributes = True

# Schema for user response with additional fields for read operations
class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True

# Lightweight profile for user responses
class UserProfile(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True

# Schema for user login request
class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @validator("password")
    def require_username_or_email(cls, v, values):
        if not values.get("email") and not values.get("username"):
            raise ValueError("Either 'email' or 'username' must be provided.")
        return v

# Schema for returning authentication tokens
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for token data, to be included in protected routes
class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# Schema for user information stored in the database
class UserInDB(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True

# Schema for reset password request
class PasswordResetRequest(BaseModel):
    email: EmailStr

# Schema for resetting the password using token
class PasswordReset(BaseModel):
    reset_token: str
    new_password: str

# Read-only schema for user information
class UserRead(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True
