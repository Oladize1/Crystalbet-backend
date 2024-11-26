from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Base model for user representation in the application
class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    
    # Example method to fetch user by username if using MongoDB or similar
    @classmethod
    async def get_user_by_username(cls, username: str):
        # Logic to query the database for the user by username
        pass
class UserModel(BaseModel):
    id: Optional[str]  # This would usually be the ObjectId in MongoDB, but represented as a string here
    username: str = Field(..., min_length=3)
    email: EmailStr  # Pydantic's EmailStr for validating email addresses
    
    class Config:
        from_attributes = True  # Enables ORM compatibility for models like MongoDB or SQLAlchemy

# Model for updating user details
class UserUpdateModel(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr]
    
    class Config:
        from_attributes = True  # Inherits the same settings

# Model for user information in the database, including hashed passwords and admin status
class UserInDB(UserModel):
    hashed_password: str  # Hashed password stored in the database
    is_active: bool = True
    is_superuser: bool = False
    
    class Config:
        from_attributes = True  # Compatibility with ORMs
