from pydantic import BaseModel, Field, condecimal
from datetime import datetime

class Coupon(BaseModel):
    code: str = Field(..., description="Unique coupon code")  # Unique coupon code
    discount: condecimal(gt=0)  # Ensures discount is positive
    expiry_date: datetime  # Expiry date of the coupon

    def is_expired(self) -> bool:
        """Check if the coupon has expired."""
        return datetime.now() > self.expiry_date

    class Config:
        json_schema_extra = {
            "example": {
                "code": "SAVE20",
                "discount": 20.0,  # Ensure this is a float
                "expiry_date": "2024-12-31T23:59:59"  # Use a valid ISO format for datetime
            }
        }

# Test the Coupon model
try:
    # Example of valid data
    coupon = Coupon(code="SAVE20", discount=20.0, expiry_date=datetime(2024, 12, 31, 23, 59, 59))
    print(coupon.model_dump_json())  # Use model_dump_json() to get JSON output

    # Example of invalid data (should raise an error)
    invalid_coupon = Coupon(code="SAVE30", discount=-10.0, expiry_date=datetime(2024, 12, 31, 23, 59, 59))
except ValueError as e:
    print(f"Error: {e}")
