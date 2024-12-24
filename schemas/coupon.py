from pydantic import BaseModel, Field
from datetime import date

# Schema for creating a new coupon
class CouponCheckResponse(BaseModel):
    code: str = Field(..., min_length=1, description="Unique code for the coupon")
    discount: float = Field(..., gt=0, description="Discount value for the coupon")
    expiry_date: str = Field(..., description="Expiry date for the coupon in YYYY-MM-DD format")

# Schema for checking the validity of a coupon
class CouponCheckRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Unique code for the coupon to check")
