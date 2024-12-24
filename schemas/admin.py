from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AdminContentBase(BaseModel):
    title: str = Field(..., example="Sample Title")
    description: str = Field(..., example="Sample Description")

class AdminContentCreate(AdminContentBase):
    pass

class AdminContentUpdate(AdminContentBase):
    title: Optional[str] = Field(None, example="Updated Title")  # Optional to allow partial updates
    description: Optional[str] = Field(None, example="Updated Description")  # Optional for updates

class AdminContent(AdminContentBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Automatically set creation date
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # Automatically set update date

    class Config:
        from_attributes = True  # Allows attribute population from class attributes
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Serialize datetime to ISO format
        }

# Example Usage
if __name__ == "__main__":
    # Creating an admin content instance
    content_data = {
        "title": "My First Admin Content",
        "description": "This is a description for the admin content."
    }
    
    new_content = AdminContentCreate(**content_data)
    print(new_content.json())  # Serialize to JSON
