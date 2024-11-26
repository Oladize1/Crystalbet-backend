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

class Payment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    amount: condecimal(gt=0)  # Ensure amount is greater than 0
    currency: str
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True  # Allow PyObjectId type
        json_encoders = {
            ObjectId: str  # Encoder for BSON ObjectId
        }

# Example usage
if __name__ == "__main__":
    payment_data = {
        "user_id": "user123",
        "amount": 150.00,
        "currency": "USD",
        "status": "completed",
        "transaction_id": "txn_abc123"
    }

    payment = Payment(**payment_data)
    print(payment.model_dump_json())  # Serialize to JSON
