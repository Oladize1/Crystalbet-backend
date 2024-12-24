from pydantic import BaseModel, Field
from typing import Optional

class TransactionCreate(BaseModel):
    amount: float
    status: str  # e.g., 'completed', 'pending', 'failed'

class TransactionResponse(BaseModel):
    id: str = Field(..., alias="_id")  # Assuming you want to use alias for MongoDB ObjectId
    user_id: str
    amount: float
    status: str
    created_at: str  # Consider using a datetime type if you're working with timestamps

    class Config:
        populate_by_name = True  # Allows using field names directly
        from_attributes = True  # Allows populating from attributes in response models
