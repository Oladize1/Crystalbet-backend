# services/coupon.py

from typing import Optional
from mongoengine import DoesNotExist
from datetime import datetime
from fastapi import HTTPException, status
from db.mongodb import get_db
from models.coupon import Coupon
class CouponService:
    @staticmethod
    def create_coupon(coupon_data):
        from schemas.coupon import CouponCreate  # Move import here to avoid circular import
        """Create a new coupon and save it to the database."""
        try:
            # Parse the expiry date from the provided string format
            expiry_date = datetime.strptime(coupon_data.expiry_date, "%Y-%m-%d")
            
            # Create a new Coupon instance
            coupon = Coupon(
                code=coupon_data.code,
                discount=coupon_data.discount,
                expiry_date=expiry_date
            )
            
            # Save the coupon to the database
            coupon.save()
            return coupon
        except Exception as e:
            # Log the exception or raise an error (logging can be implemented as needed)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def validate_coupon(coupon_data):
        from schemas.coupon import CouponCheck  # Move import here to avoid circular import
        """Validate the given coupon code and check if it is expired."""
        try:
            # Retrieve the coupon using the provided code
            coupon = Coupon.objects.get(code=coupon_data.code)
            
            # Check if the coupon is expired
            if coupon.is_expired():
                return None
            
            return coupon
        except DoesNotExist:
            # Coupon does not exist; return None
            return None
        except Exception as e:
            # Handle other potential exceptions
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
