from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from bson import ObjectId
from typing import Optional

# Custom type for MongoDB ObjectId handling with Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

# Pydantic BaseModel for User Data
class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")  # MongoDB stores _id, but we map it to id for convenience
    username: str
    email: EmailStr
    password: str  # Store hashed password
    created_at: datetime
    is_active: bool
    is_superuser: bool

    class Config:
        allow_population_by_field_name = True  # Enables usage of "id" instead of "_id"
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string for serialization
        }

# Model for User Creation (input data for user registration)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Model for User Update (input data for updating existing user information)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Model for User Login (input data for logging in, but we won't include the password in the response)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Model for resetting user password (input data for password reset flow)
class UserPasswordReset(BaseModel):
    password: str
    confirm_password: str

