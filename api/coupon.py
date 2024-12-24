from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from pymongo.collection import Collection
from typing import Any, Optional
from datetime import datetime
from db.mongodb import get_db
from models.coupon import CouponModel  # Assuming a CouponModel schema exists in models

router = APIRouter()

class CouponCheckRequest(BaseModel):
    code: str

class CouponResponse(BaseModel):
    code: str
    is_valid: bool
    discount_amount: Optional[float] = None
    message: str

def find_coupon_by_code(db: Collection, code: str) -> Optional[CouponResponse]:
    coupon = db.find_one({"code": code})
    if coupon:
        if coupon["expires_at"] < datetime.utcnow() or not coupon["is_active"]:
            return CouponResponse(
                code=code,
                is_valid=False,
                message="Coupon is expired or inactive"
            )
        return CouponResponse(
            code=code,
            is_valid=True,
            discount_amount=coupon["discount_amount"],
            message="Coupon is valid"
        )
    return CouponResponse(
        code=code,
        is_valid=False,
        message="Invalid coupon code"
    )

@router.post("/check", response_model=CouponResponse, status_code=status.HTTP_200_OK)
async def check_coupon(
    request: CouponCheckRequest,
    db: Collection = Depends(lambda: get_db("coupons"))
) -> Any:
    coupon_response = find_coupon_by_code(db, request.code)
    if not coupon_response.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=coupon_response.message
        )
    return coupon_response
