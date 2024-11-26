from pydantic import BaseModel, Field, condecimal, ConfigDict
from bson import ObjectId
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class CouponModel(BaseModel):
    code: str = Field(..., unique=True)  # Unique coupon code
    discount: condecimal(gt=0)  # Ensures discount is positive
    expiry_date: datetime  # Expiry date of the coupon

    class Config:
        json_encoders = {
            ObjectId: str
        }
        # Set the correct configuration options
        arbitrary_types_allowed = True  # Allow PyObjectId type

    def is_expired(self) -> bool:
        """Check if the coupon has expired."""
        return datetime.now() > self.expiry_date

    @classmethod
    def model_validate(cls, value):
        return cls.validate(value)

# Example usage
if __name__ == "__main__":
    coupon_data = {
        "code": "SAVE20",
        "discount": 20.0,
        "expiry_date": "2024-12-31T23:59:59"
    }

    coupon = Coupon(**coupon_data)
    print(coupon.model_dump_json())  # Serialize to JSON
