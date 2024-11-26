from pydantic import BaseModel, Field, condecimal
from bson import ObjectId
from datetime import datetime
from typing import Optional

# Custom ObjectId type for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class TransactionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")  # MongoDB ObjectId
    user_id: str
    amount: condecimal(gt=0)  # Ensure amount is greater than 0
    status: str  # e.g., 'completed', 'pending', 'failed'
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Automatically set to current datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string for JSON serialization
        }

# Example usage
if __name__ == "__main__":
    transaction_data = {
        "user_id": "user123",
        "amount": 150.00,
        "status": "completed"
    }

    transaction = Transaction(**transaction_data)
    print(transaction.model_dump_json())  # Serialize to JSON
