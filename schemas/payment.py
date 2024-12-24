from pydantic import BaseModel, Field
from typing import Optional

class PaymentCreate(BaseModel):
    user_id: str
    amount: float
    currency: str

class PaymentResponse(BaseModel):
    id: str = Field(..., alias="_id")  # Using alias for the ObjectId
    user_id: str
    amount: float
    currency: str
    status: str
    transaction_id: Optional[str] = None  # Optional field
    created_at: str

    class Config:
        # Enable field population using aliases
        populate_by_name = True
        json_encoders = {
            # Custom JSON encoders if needed
        }
